package demo.sso;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.*;
@SpringBootTest(properties={"PUBLIC_URL=http://localhost:8080","OTHER_APP_URL=http://localhost:8081","CASDOOR_URL=https://example.invalid","CLIENT_ID=test","CLIENT_SECRET=test","COOKIE_SECURE=false"})
@AutoConfigureMockMvc class SecurityTest {
 @Autowired MockMvc mvc;
 @Test void protectedApiAndIdentity()throws Exception{mvc.perform(get("/api/business")).andExpect(status().isUnauthorized());mvc.perform(get("/api/me")).andExpect(status().isOk()).andExpect(jsonPath("$.authenticated").value(false));mvc.perform(get("/api/business").with(oidcLogin())).andExpect(status().isOk()).andExpect(jsonPath("$[0].id").value("BKG-2026-0101"));}
 @Test void logoutRequiresCsrf()throws Exception{mvc.perform(post("/logout")).andExpect(status().isForbidden());mvc.perform(post("/logout").with(csrf())).andExpect(status().is3xxRedirection());}
}
