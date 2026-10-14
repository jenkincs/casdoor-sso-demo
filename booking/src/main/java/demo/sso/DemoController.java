package demo.sso;
import java.util.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.core.oidc.user.OidcUser;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.web.bind.annotation.*;
@RestController public class DemoController {
 @Value("${demo.public-url}") String publicUrl;
 @Value("${demo.other-app-url}") String otherUrl;
 @GetMapping("/health") Map<String,String> health(){return Map.of("status","ok","app","booking");}
 @GetMapping("/api/config") Map<String,String> config(){return Map.of("app","booking","publicUrl",publicUrl,"otherAppUrl",otherUrl,"loginUrl","/oauth2/authorization/casdoor");}
 @GetMapping("/api/me") Map<String,Object> me(Authentication auth,CsrfToken csrf){Map<String,Object> out=new LinkedHashMap<>();boolean logged=auth!=null&&auth.getPrincipal() instanceof OidcUser;out.put("authenticated",logged);out.put("csrfToken",csrf.getToken());out.put("csrfParameter",csrf.getParameterName());if(logged){OidcUser u=(OidcUser)auth.getPrincipal();out.put("subject",u.getSubject());out.put("username",Objects.toString(u.getPreferredUsername(),u.getSubject()));out.put("displayName",Objects.toString(u.getFullName(),Objects.toString(u.getPreferredUsername(),u.getSubject())));}return out;}
 @GetMapping("/api/business") List<Map<String,String>> business(){return List.of(Map.of("id","BKG-2026-0101","detail","上海 → 新加坡","status","已确认"),Map.of("id","BKG-2026-0102","detail","深圳 → 汉堡","status","处理中"),Map.of("id","BKG-2026-0103","detail","宁波 → 洛杉矶","status","已确认"));}
}
