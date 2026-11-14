package com.cesde.proyectointegrador.modules.graficas.controller;

// NUEVO: ENDPOINTS QUE ENTREGAN LAS GRAFICAS COMO IMAGEN PNG (LOS CONSUME EL FRONTEND Y graficas.html)

import com.cesde.proyectointegrador.modules.graficas.service.GraficaService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.CacheControl;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/graficas")
public class GraficaController {

    @Autowired
    private GraficaService graficaService;

    // NUEVO: RESPUESTA PNG SIN CACHE PARA QUE SIEMPRE MUESTRE LOS DATOS ACTUALES
    private ResponseEntity<byte[]> png(byte[] imagen) {
        return ResponseEntity.ok()
                .contentType(MediaType.IMAGE_PNG)
                .cacheControl(CacheControl.noStore())
                .body(imagen);
    }

    // ====================================================================
    // NUEVO: SOLO ADMINISTRADOR
    // ====================================================================

    @GetMapping("/admin/estudiantes")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<byte[]> adminEstudiantes() {
        return png(graficaService.graficaAdminEstudiantes());
    }

    @GetMapping("/admin/retos-estado")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<byte[]> adminRetosEstado() {
        return png(graficaService.graficaAdminRetosEstado());
    }

    @GetMapping("/admin/retos-tomados")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<byte[]> adminRetosTomados() {
        return png(graficaService.graficaAdminRetosTomados());
    }

    @GetMapping("/admin/empresas")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<byte[]> adminEmpresas() {
        return png(graficaService.graficaAdminEmpresas());
    }

    // ====================================================================
    // NUEVO: SOLO ESTUDIANTE / DEV (SIEMPRE SUS PROPIOS RETOS, TOMADOS DEL TOKEN)
    // ====================================================================

    @GetMapping("/estudiante/mis-retos")
    @PreAuthorize("hasRole('USUARIO')")
    public ResponseEntity<byte[]> estudianteMisRetos(Authentication authentication) {
        return png(graficaService.graficaEstudianteMisRetos(authentication.getName()));
    }
}
