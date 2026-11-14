package com.cesde.proyectointegrador.modules.graficas.service;

// NUEVO: SERVICIO QUE ARMA LOS DATOS DE LAS GRAFICAS Y LE PIDE LA IMAGEN AL SERVICIO PYTHON (MATPLOTLIB)

import com.cesde.proyectointegrador.modules.empresas.entity.Empresa;
import com.cesde.proyectointegrador.modules.empresas.repository.EmpresaRepository;
import com.cesde.proyectointegrador.modules.registros.entity.Registro;
import com.cesde.proyectointegrador.modules.registros.repository.RegistroRepository;
import com.cesde.proyectointegrador.modules.retos.entity.Reto;
import com.cesde.proyectointegrador.modules.retos.repository.RetoRepository;
import com.cesde.proyectointegrador.modules.usuarios.entity.Usuario;
import com.cesde.proyectointegrador.modules.usuarios.repository.UsuarioRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.server.ResponseStatusException;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class GraficaService {

    // NUEVO: REGLA PARA CONTAR UN RETO COMO "TOMADO": REGISTROS DE TIPO INSCRIPCION O ENTREGA (SE EXCLUYEN LOS RECHAZADOS)
    private static final Set<String> TIPOS_TOMADO = Set.of("INSCRIPCION", "ENTREGA");

    // NUEVO: ORDEN FIJO DE LOS ESTADOS DE UN RETO
    private static final List<String> ESTADOS_RETO = List.of("ABIERTO", "EN_PROGRESO", "CERRADO", "FINALIZADO");

    // NUEVO: CANTIDAD MAXIMA DE FILAS EN CADA GRAFICA PARA QUE SE MANTENGA LEGIBLE
    private static final int MAX_ESTUDIANTES = 15;
    private static final int MAX_RETOS = 10;
    private static final int MAX_EMPRESAS = 10;

    @Autowired
    private UsuarioRepository usuarioRepository;

    @Autowired
    private RegistroRepository registroRepository;

    @Autowired
    private RetoRepository retoRepository;

    @Autowired
    private EmpresaRepository empresaRepository;

    // NUEVO: DIRECCION DEL SERVICIO PYTHON (SE PUEDE CAMBIAR CON LA VARIABLE DE ENTORNO APP_GRAFICAS_URL)
    @Value("${app.graficas.url:http://localhost:5000}")
    private String graficasUrl;

    // NUEVO: CLAVE OPCIONAL COMPARTIDA CON EL SERVICIO PYTHON (VARIABLE DE ENTORNO APP_GRAFICAS_KEY)
    @Value("${app.graficas.key:}")
    private String graficasKey;

    // NUEVO: UN RETO TOMADO POR UN ESTUDIANTE (SIN IMPORTAR CUANTOS REGISTROS TENGA)
    private static class Participacion {
        final Usuario usuario;
        final Reto reto;
        boolean culminado = false;

        Participacion(Usuario usuario, Reto reto) {
            this.usuario = usuario;
            this.reto = reto;
        }
    }

    // NUEVO: CALCULA LOS RETOS TOMADOS. SI ALGUN REGISTRO ESTA COMPLETADO ES CULMINADO, SI NO ESTA EN PROCESO
    private List<Participacion> participaciones() {
        Map<String, Participacion> mapa = new LinkedHashMap<>();
        for (Registro r : registroRepository.findAll()) {
            if (r.getUsuario() == null || r.getReto() == null) continue;
            if (!"USUARIO".equals(r.getUsuario().getRol())) continue;
            if (!TIPOS_TOMADO.contains(r.getTipo())) continue;
            if ("RECHAZADO".equals(r.getEstado())) continue;

            String clave = r.getUsuario().getId() + "-" + r.getReto().getId();
            Participacion p = mapa.computeIfAbsent(clave, k -> new Participacion(r.getUsuario(), r.getReto()));
            if ("COMPLETADO".equals(r.getEstado())) {
                p.culminado = true;
            }
        }
        return new ArrayList<>(mapa.values());
    }

    private static String nombreCompleto(Usuario u) {
        return (u.getNombre() + " " + u.getApellido()).trim();
    }

    // ====================================================================
    // NUEVO: PANEL DE ADMINISTRACION
    // ====================================================================

    // NUEVO: GRAFICA DE ESTUDIANTES / DEVS
    public byte[] graficaAdminEstudiantes() {
        List<Usuario> estudiantes = usuarioRepository.findAll().stream()
                .filter(u -> "USUARIO".equals(u.getRol()))
                .collect(Collectors.toList());

        long activos = estudiantes.stream().filter(u -> "ACTIVO".equals(u.getEstado())).count();

        Map<Integer, int[]> conteo = new HashMap<>();
        for (Participacion p : participaciones()) {
            int[] c = conteo.computeIfAbsent(p.usuario.getId(), k -> new int[2]);
            if (p.culminado) c[1]++; else c[0]++;
        }

        List<Map<String, Object>> filas = estudiantes.stream()
                .filter(u -> conteo.containsKey(u.getId()))
                .sorted((a, b) -> {
                    int[] ca = conteo.get(a.getId());
                    int[] cb = conteo.get(b.getId());
                    int cmp = Integer.compare(cb[0] + cb[1], ca[0] + ca[1]);
                    return cmp != 0 ? cmp : nombreCompleto(a).compareToIgnoreCase(nombreCompleto(b));
                })
                .limit(MAX_ESTUDIANTES)
                .map(u -> {
                    int[] c = conteo.get(u.getId());
                    Map<String, Object> fila = new LinkedHashMap<>();
                    fila.put("nombre", nombreCompleto(u));
                    fila.put("enProceso", c[0]);
                    fila.put("culminados", c[1]);
                    return fila;
                })
                .collect(Collectors.toList());

        Map<String, Object> datos = new LinkedHashMap<>();
        datos.put("totalEstudiantes", estudiantes.size());
        datos.put("activos", activos);
        datos.put("inactivos", estudiantes.size() - activos);
        datos.put("estudiantes", filas);
        return renderizar("admin-estudiantes", datos);
    }

    // NUEVO: GRAFICA DE RETOS EN TOTAL POR ESTADO
    public byte[] graficaAdminRetosEstado() {
        List<Reto> retos = retoRepository.findAll();
        Map<String, Integer> estados = new LinkedHashMap<>();
        ESTADOS_RETO.forEach(e -> estados.put(e, 0));
        for (Reto r : retos) {
            estados.merge(r.getEstado(), 1, Integer::sum);
        }

        Map<String, Object> datos = new LinkedHashMap<>();
        datos.put("total", retos.size());
        datos.put("estados", estados);
        return renderizar("admin-retos-estado", datos);
    }

    // NUEVO: GRAFICA DE RETOS TOMADOS, EN PROCESO Y CULMINADOS
    public byte[] graficaAdminRetosTomados() {
        List<Participacion> lista = participaciones();
        int enProceso = 0;
        int culminados = 0;
        Map<Integer, int[]> porReto = new HashMap<>();
        Map<Integer, String> titulos = new HashMap<>();
        for (Participacion p : lista) {
            int[] c = porReto.computeIfAbsent(p.reto.getId(), k -> new int[2]);
            titulos.put(p.reto.getId(), p.reto.getTitulo());
            if (p.culminado) { culminados++; c[1]++; } else { enProceso++; c[0]++; }
        }

        List<Map<String, Object>> filas = porReto.entrySet().stream()
                .sorted((a, b) -> Integer.compare(b.getValue()[0] + b.getValue()[1], a.getValue()[0] + a.getValue()[1]))
                .limit(MAX_RETOS)
                .map(e -> {
                    Map<String, Object> fila = new LinkedHashMap<>();
                    fila.put("titulo", titulos.get(e.getKey()));
                    fila.put("enProceso", e.getValue()[0]);
                    fila.put("culminados", e.getValue()[1]);
                    return fila;
                })
                .collect(Collectors.toList());

        Map<String, Object> datos = new LinkedHashMap<>();
        datos.put("tomados", lista.size());
        datos.put("enProceso", enProceso);
        datos.put("culminados", culminados);
        datos.put("retos", filas);
        return renderizar("admin-retos-tomados", datos);
    }

    // NUEVO: GRAFICA DE EMPRESAS PATROCINADORAS
    public byte[] graficaAdminEmpresas() {
        List<Reto> retos = retoRepository.findAll();
        List<Participacion> participaciones = participaciones();

        List<Map<String, Object>> filas = new ArrayList<>();
        for (Empresa e : empresaRepository.findAll()) {
            Map<String, Integer> porEstado = new LinkedHashMap<>();
            ESTADOS_RETO.forEach(s -> porEstado.put(s, 0));
            int totalRetos = 0;
            for (Reto r : retos) {
                if (r.getEmpresa() != null && Objects.equals(r.getEmpresa().getId(), e.getId())) {
                    porEstado.merge(r.getEstado(), 1, Integer::sum);
                    totalRetos++;
                }
            }
            if (totalRetos == 0) continue;

            int enProceso = 0;
            int culminados = 0;
            for (Participacion p : participaciones) {
                if (p.reto.getEmpresa() != null && Objects.equals(p.reto.getEmpresa().getId(), e.getId())) {
                    if (p.culminado) culminados++; else enProceso++;
                }
            }

            Map<String, Object> fila = new LinkedHashMap<>();
            fila.put("nombre", e.getNombre());
            fila.put("retosPorEstado", porEstado);
            fila.put("totalRetos", totalRetos);
            fila.put("enProceso", enProceso);
            fila.put("culminados", culminados);
            filas.add(fila);
        }

        filas.sort((a, b) -> Integer.compare((Integer) b.get("totalRetos"), (Integer) a.get("totalRetos")));
        List<Map<String, Object>> top = filas.stream().limit(MAX_EMPRESAS).collect(Collectors.toList());

        Map<String, Object> datos = new LinkedHashMap<>();
        datos.put("empresas", top);
        return renderizar("admin-empresas", datos);
    }

    // ====================================================================
    // NUEVO: AREA DE ESTUDIANTES / DEVS (SOLO LOS RETOS DEL USUARIO AUTENTICADO)
    // ====================================================================

    public byte[] graficaEstudianteMisRetos(String email) {
        Usuario usuario = usuarioRepository.findByEmailIgnoreCase(email == null ? "" : email.trim())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Usuario no encontrado"));

        int enProceso = 0;
        int culminados = 0;
        int puntosGanados = 0;
        List<Map<String, Object>> retos = new ArrayList<>();
        for (Participacion p : participaciones()) {
            if (!Objects.equals(p.usuario.getId(), usuario.getId())) continue;
            int puntos = p.reto.getPuntos() != null ? p.reto.getPuntos() : 0;
            if (p.culminado) { culminados++; puntosGanados += puntos; } else { enProceso++; }

            Map<String, Object> fila = new LinkedHashMap<>();
            fila.put("titulo", p.reto.getTitulo());
            fila.put("puntos", puntos);
            fila.put("culminado", p.culminado);
            retos.add(fila);
        }

        Map<String, Object> datos = new LinkedHashMap<>();
        datos.put("nombre", nombreCompleto(usuario));
        datos.put("enProceso", enProceso);
        datos.put("culminados", culminados);
        datos.put("puntosGanados", puntosGanados);
        datos.put("retos", retos);
        return renderizar("estudiante-mis-retos", datos);
    }

    // ====================================================================
    // NUEVO: COMUNICACION CON EL SERVICIO PYTHON
    // ====================================================================

    private byte[] renderizar(String nombre, Map<String, Object> datos) {
        // NUEVO: TIEMPOS DE ESPERA CORTOS PARA NO DEJAR LA PETICION COLGADA SI PYTHON NO RESPONDE
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(3000);
        factory.setReadTimeout(15000);
        RestTemplate rest = new RestTemplate(factory);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setAccept(List.of(MediaType.IMAGE_PNG));
        if (graficasKey != null && !graficasKey.isBlank()) {
            headers.set("X-Graficas-Key", graficasKey);
        }

        try {
            byte[] png = rest.postForObject(graficasUrl + "/render/" + nombre, new HttpEntity<>(datos, headers), byte[].class);
            if (png == null || png.length == 0) {
                throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "El servicio de gráficas devolvió una imagen vacía");
            }
            return png;
        } catch (RestClientException ex) {
            throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE,
                    "El servicio de gráficas (Python) no está disponible. Inícialo en " + graficasUrl);
        }
    }
}
