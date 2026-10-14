import express from 'express';
import session from 'express-session';
import memorystore from 'memorystore';
import helmet from 'helmet';
import * as oidc from 'openid-client';
import { randomBytes, timingSafeEqual } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

export function createApp(env = process.env) {
  for (const key of ['PUBLIC_URL','CASDOOR_URL','CLIENT_ID','CLIENT_SECRET','SESSION_SECRET','OTHER_APP_URL']) if(!env[key]) throw new Error(`Missing ${key}`);
  const app = express(), production = env.NODE_ENV === 'production', Store = memorystore(session);
  const store = new Store({ checkPeriod: 60000 });
  app.set('trust proxy', 1);
  app.use(helmet({ contentSecurityPolicy: { directives: { defaultSrc:["'self'"],scriptSrc:["'self'"],styleSrc:["'self'","'unsafe-inline'",'https://fonts.googleapis.com'],fontSrc:["'self'",'https://fonts.gstatic.com'],imgSrc:["'self'",'data:'],connectSrc:["'self'"] } } }));
  app.use(express.urlencoded({extended:false}));
  app.use(session({ name:'invoice.sid', secret:env.SESSION_SECRET, store, resave:false, saveUninitialized:false, cookie:{httpOnly:true,secure:production,sameSite:'lax',maxAge:12*60*60*1000} }));
  app.use((req,res,next)=>{ res.set('Cache-Control','no-store'); next(); });
  let configPromise;
  const configuration = () => configPromise ||= oidc.discovery(new URL(env.CASDOOR_URL),env.CLIENT_ID,env.CLIENT_SECRET,oidc.ClientSecretPost).catch(e=>{configPromise=undefined;throw e;});
  const csrf = req => req.session.csrf ||= randomBytes(24).toString('hex');
  app.get('/health',(_req,res)=>res.json({status:'ok',app:'invoice'}));
  app.get('/api/config',(_req,res)=>res.json({app:'invoice',publicUrl:env.PUBLIC_URL,otherAppUrl:env.OTHER_APP_URL,loginUrl:'/login'}));
  app.get('/api/me',(req,res)=>res.json({authenticated:!!req.session.user,...req.session.user,csrfToken:csrf(req),csrfParameter:'_csrf'}));
  app.get('/api/business',(req,res)=>{if(!req.session.user)return res.status(401).json({error:'authentication_required'});res.json([{id:'INV-2026-0101',detail:'USD 2,480.00',status:'待支付'},{id:'INV-2026-0102',detail:'USD 1,650.00',status:'已支付'},{id:'INV-2026-0103',detail:'USD 3,120.00',status:'待支付'}]);});
  app.get('/login',async(req,res,next)=>{try{const config=await configuration();const verifier=oidc.randomPKCECodeVerifier(),state=oidc.randomState(),nonce=oidc.randomNonce();req.session.oauth={verifier,state,nonce,started:Date.now()};const url=oidc.buildAuthorizationUrl(config,{redirect_uri:`${env.PUBLIC_URL}/callback`,scope:'openid profile email',code_challenge:await oidc.calculatePKCECodeChallenge(verifier),code_challenge_method:'S256',state,nonce});req.session.save(err=>err?next(err):res.redirect(url.href));}catch(e){next(e);}});
  app.get('/callback',async(req,res,next)=>{const pending=req.session.oauth;delete req.session.oauth;try{if(!pending||Date.now()-pending.started>600000)throw new Error('Missing or expired login request');const config=await configuration();const tokens=await oidc.authorizationCodeGrant(config,new URL(req.originalUrl,env.PUBLIC_URL),{pkceCodeVerifier:pending.verifier,expectedState:pending.state,expectedNonce:pending.nonce,idTokenExpected:true});const claims=tokens.claims();if(!claims?.sub)throw new Error('Missing subject');const info=await oidc.fetchUserInfo(config,tokens.access_token,claims.sub);req.session.regenerate(err=>{if(err)return next(err);req.session.user={subject:claims.sub,username:info.preferred_username||info.name||claims.sub,displayName:info.name||info.preferred_username||claims.sub};req.session.save(err=>err?next(err):res.redirect('/'));});}catch(e){next(e);}});
  app.post('/logout',(req,res)=>{const expected=req.session.csrf||'',received=String(req.body._csrf||'');if(!expected||expected.length!==received.length||!timingSafeEqual(Buffer.from(expected),Buffer.from(received)))return res.status(403).json({error:'invalid_csrf'});req.session.destroy(err=>{if(err)return res.status(500).json({error:'logout_failed'});res.clearCookie('invoice.sid',{httpOnly:true,secure:production,sameSite:'lax',path:'/'});res.redirect('/');});});
  app.use(express.static(fileURLToPath(new URL('./public',import.meta.url))));
  app.get('/',(_req,res)=>res.sendFile(fileURLToPath(new URL('./public/index.html',import.meta.url))));
  app.use((err,_req,res,_next)=>{console.error('OIDC request failed:',err.code||err.name);res.redirect('/?error=login');});
  app.locals.close = () => store.stopInterval();
  return app;
}
if(process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){const app=createApp();const server=app.listen(Number(process.env.PORT||8081),'0.0.0.0',()=>console.log('Invoice listening'));process.on('SIGTERM',()=>server.close(()=>{app.locals.close();process.exit(0);}));}
