import test from 'node:test';
import assert from 'node:assert/strict';
import {createApp} from './server.js';
test('unauthenticated API denies data and logout requires valid CSRF',async()=>{
 const app=createApp({PUBLIC_URL:'http://localhost:8081',CASDOOR_URL:'https://example.invalid',CLIENT_ID:'test',CLIENT_SECRET:'test',SESSION_SECRET:'test-only-secret-must-be-long-enough',OTHER_APP_URL:'http://localhost:8080'});
 const server=app.listen(0,'127.0.0.1');await new Promise(resolve=>server.once('listening',resolve));const base=`http://127.0.0.1:${server.address().port}`;
 try{assert.equal((await fetch(base+'/api/business')).status,401);const response=await fetch(base+'/api/me');const me=await response.json();assert.equal(me.authenticated,false);assert.ok(me.csrfToken);const cookie=response.headers.get('set-cookie').split(';')[0];assert.equal((await fetch(base+'/logout',{method:'POST',headers:{cookie,'content-type':'application/x-www-form-urlencoded'},body:'_csrf=bad'})).status,403);const logout=await fetch(base+'/logout',{method:'POST',headers:{cookie,'content-type':'application/x-www-form-urlencoded'},body:new URLSearchParams({_csrf:me.csrfToken}),redirect:'manual'});assert.equal(logout.status,302);assert.equal(logout.headers.get('location'),'/');}
 finally{await new Promise(resolve=>server.close(resolve));app.locals.close();}
});
