ranking_query = """
   WITH partidos_nombres AS (
        SELECT
            p.ID_MATCH,
            el.Nombre AS Local,
            ev.Nombre AS Visita,
            p.Goles_Local,
            p.Goles_Visita
        FROM Partidos p
        JOIN Equipos el ON p.Local_ID = el.ID_TEAM
        JOIN Equipos ev ON p.Visita_ID = ev.ID_TEAM
    ),
    stats_local AS (
        SELECT 
            Local AS equipo,
            COUNT(*) FILTER (WHERE Goles_Local > Goles_Visita) AS ganados_local,
            COUNT(*) FILTER (WHERE Goles_Local < Goles_Visita) AS derrotas_local,
            COUNT(*) FILTER (WHERE Goles_Local = Goles_Visita) AS empates_local,
            SUM(Goles_Local) AS gf_local,
            SUM(Goles_Visita) AS gc_local
        FROM partidos_nombres
        GROUP BY Local
    ),
    stats_visita AS (
        SELECT 
            Visita AS equipo,
            COUNT(*) FILTER (WHERE Goles_Visita > Goles_Local) AS ganados_visita,
            COUNT(*) FILTER (WHERE Goles_Visita < Goles_Local) AS derrotas_visita,
            COUNT(*) FILTER (WHERE Goles_Visita = Goles_Local) AS empates_visita,
            SUM(Goles_Visita) AS gf_visita,
            SUM(Goles_Local) AS gc_visita
        FROM partidos_nombres
        GROUP BY Visita
    )
    SELECT 
        e.Nombre AS equipo,
        COALESCE(l.ganados_local,0) AS ganados_local,
        COALESCE(v.ganados_visita,0) AS ganados_visita,
        COALESCE(l.ganados_local,0) + COALESCE(v.ganados_visita,0) AS ganados,
        COALESCE(l.empates_local,0) + COALESCE(v.empates_visita,0) AS empates,
        COALESCE(l.derrotas_local,0) AS derrotas_local,
        COALESCE(v.derrotas_visita,0) AS derrotas_visita,
        COALESCE(l.derrotas_local,0) + COALESCE(v.derrotas_visita,0) AS derrotas,
        COALESCE(l.gf_local,0) + COALESCE(v.gf_visita,0) AS gf,
        COALESCE(l.gc_local,0) + COALESCE(v.gc_visita,0) AS gc,
        (COALESCE(l.gf_local,0) + COALESCE(v.gf_visita,0)) - (COALESCE(l.gc_local,0) + COALESCE(v.gc_visita,0)) AS diferencia_goles,
        (COALESCE(l.ganados_local,0) + COALESCE(v.ganados_visita,0)) * 3 +
        (COALESCE(l.empates_local,0) + COALESCE(v.empates_visita,0)) AS puntos,
        ROUND(
            ((COALESCE(l.ganados_local,0) + COALESCE(v.ganados_visita,0)) * 3 +
            (COALESCE(l.empates_local,0) + COALESCE(v.empates_visita,0)))::numeric / 
            (GREATEST((COALESCE(l.ganados_local,0) + COALESCE(v.ganados_visita,0) +
              COALESCE(l.derrotas_local,0) + COALESCE(v.derrotas_visita,0) +
              COALESCE(l.empates_local,0) + COALESCE(v.empates_visita,0))*3,1)) * 100, 2
        ) AS porcentaje_rendimiento,
        (COALESCE(l.ganados_local,0) + COALESCE(v.ganados_visita,0) +
         COALESCE(l.derrotas_local,0) + COALESCE(v.derrotas_visita,0) +
         COALESCE(l.empates_local,0) + COALESCE(v.empates_visita,0)) AS partidos_jugados
    FROM Equipos e
    LEFT JOIN stats_local l ON e.Nombre = l.equipo
    LEFT JOIN stats_visita v ON e.Nombre = v.equipo
    ORDER BY e.Nombre;
"""

headtohead_query = """
WITH params AS (SELECT %(eq1)s::INT AS equipo1_id, %(eq2)s::INT AS equipo2_id)
SELECT
    COUNT(*) AS partidos,
    SUM(CASE WHEN (p.Local_ID=params.equipo1_id AND p.Goles_Local>p.Goles_Visita) OR
                  (p.Visita_ID=params.equipo1_id AND p.Goles_Visita>p.Goles_Local)
             THEN 1 ELSE 0 END) AS ganados1,
    SUM(CASE WHEN p.Goles_Local=p.Goles_Visita THEN 1 ELSE 0 END) AS empates,
    SUM(CASE WHEN (p.Local_ID=params.equipo2_id AND p.Goles_Local>p.Goles_Visita) OR
                  (p.Visita_ID=params.equipo2_id AND p.Goles_Visita>p.Goles_Local)
             THEN 1 ELSE 0 END) AS ganados2,
    SUM(CASE WHEN p.Local_ID=params.equipo1_id THEN p.Goles_Local
             WHEN p.Visita_ID=params.equipo1_id THEN p.Goles_Visita END) AS gf1,
    SUM(CASE WHEN p.Local_ID=params.equipo2_id THEN p.Goles_Local
             WHEN p.Visita_ID=params.equipo2_id THEN p.Goles_Visita END) AS gf2,
    SUM(CASE WHEN p.Local_ID=params.equipo1_id THEN p.Goles_Local - p.Goles_Visita
             WHEN p.Visita_ID=params.equipo1_id THEN p.Goles_Visita - p.Goles_Local END) AS dg
FROM Partidos p
CROSS JOIN params
WHERE (p.Local_ID=params.equipo1_id AND p.Visita_ID=params.equipo2_id)
   OR (p.Local_ID=params.equipo2_id AND p.Visita_ID=params.equipo1_id);
"""

ultimos_partidos_query = """
SELECT Fecha,
       el.Nombre AS local,
       p.Goles_Local AS goles_local,
       ev.Nombre AS visita,
       p.Goles_Visita AS goles_visita
FROM Partidos p
JOIN Equipos el ON el.ID_TEAM = p.Local_ID
JOIN Equipos ev ON ev.ID_TEAM = p.Visita_ID
WHERE (p.Local_ID=%(eq1)s AND p.Visita_ID=%(eq2)s)
   OR (p.Local_ID=%(eq2)s AND p.Visita_ID=%(eq1)s)
ORDER BY Fecha DESC
LIMIT 5;
"""
