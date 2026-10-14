package demo.sso;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.HttpStatusEntryPoint;
import org.springframework.http.HttpStatus;
import org.springframework.security.web.util.matcher.AntPathRequestMatcher;
import org.springframework.security.oauth2.client.web.DefaultOAuth2AuthorizationRequestResolver;
import org.springframework.security.oauth2.client.web.OAuth2AuthorizationRequestCustomizers;
import org.springframework.security.oauth2.client.registration.ClientRegistrationRepository;
import org.springframework.security.oauth2.client.registration.ClientRegistration;
import org.springframework.security.oauth2.client.registration.InMemoryClientRegistrationRepository;
import org.springframework.security.oauth2.core.AuthorizationGrantType;
import org.springframework.security.oauth2.core.ClientAuthenticationMethod;
import org.springframework.beans.factory.annotation.Value;
@Configuration public class SecurityConfig {
 @Bean ClientRegistrationRepository registrations(@Value("${CASDOOR_URL}")String issuer,@Value("${PUBLIC_URL}")String publicUrl,@Value("${CLIENT_ID}")String id,@Value("${CLIENT_SECRET}")String secret){
  // Explicit metadata keeps the app available while the free identity service is asleep.
  // issuerUri still enables standard ID Token issuer validation.
  return new InMemoryClientRegistrationRepository(ClientRegistration.withRegistrationId("casdoor").clientId(id).clientSecret(secret)
   .clientAuthenticationMethod(ClientAuthenticationMethod.CLIENT_SECRET_POST).authorizationGrantType(AuthorizationGrantType.AUTHORIZATION_CODE)
   .redirectUri(publicUrl+"/login/oauth2/code/casdoor").scope("openid","profile","email").issuerUri(issuer)
   .authorizationUri(issuer+"/login/oauth/authorize").tokenUri(issuer+"/api/login/oauth/access_token")
   .userInfoUri(issuer+"/api/userinfo").userNameAttributeName("sub").jwkSetUri(issuer+"/.well-known/jwks").clientName("Casdoor").build());
 }
 @Bean SecurityFilterChain security(HttpSecurity http,ClientRegistrationRepository clients)throws Exception{
  var resolver=new DefaultOAuth2AuthorizationRequestResolver(clients,"/oauth2/authorization");resolver.setAuthorizationRequestCustomizer(OAuth2AuthorizationRequestCustomizers.withPkce());
  return http.authorizeHttpRequests(a->a.requestMatchers("/","/index.html","/assets/**","/health","/api/config","/api/me","/error").permitAll().anyRequest().authenticated())
   .exceptionHandling(e->e.defaultAuthenticationEntryPointFor(new HttpStatusEntryPoint(HttpStatus.UNAUTHORIZED),new AntPathRequestMatcher("/api/**")))
   .oauth2Login(o->o.authorizationEndpoint(a->a.authorizationRequestResolver(resolver)).defaultSuccessUrl("/",true).failureUrl("/?error=login"))
   .logout(l->l.logoutSuccessUrl("/").deleteCookies("booking.sid").invalidateHttpSession(true))
   .headers(h->h.contentSecurityPolicy(c->c.policyDirectives("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'")))
   .build();
 }
}
