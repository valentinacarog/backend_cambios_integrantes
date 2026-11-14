package com.cesde.proyectointegrador.modules.graficas.config;

// NUEVO: CADENA DE SEGURIDAD ADICIONAL SOLO PARA LA PAGINA graficas.html Y SUS ARCHIVOS ESTATICOS
// NUEVO: ASI NO SE MODIFICA SecurityConfig. LOS ENDPOINTS /api/graficas/** SIGUEN PROTEGIDOS CON JWT Y ROLES

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.annotation.Order;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
public class GraficasSecurityConfig {

    @Bean
    @Order(1)
    public SecurityFilterChain graficasEstaticosChain(HttpSecurity http) throws Exception {
        http
            .securityMatcher("/graficas.html", "/graficas/**")
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth.anyRequest().permitAll());
        return http.build();
    }
}
