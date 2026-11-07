-- ============================================================================
-- MIGRACIÓN V2: Semilla Oficial de Distritos Representativos de las 7 Provincias
-- del Departamento de Huancavelica (Ubigeo 09xxxx) y sus 7 Redes de Salud (S1/S2)
-- ============================================================================

INSERT INTO cat_ubigeo_hvc (ubigeo, provincia, distrito, red_salud, altitud_msnm, latitud, longitud, poblacion_menor_5, ruralidad_pct)
VALUES
    -- 1. Provincia de Huancavelica
    ('090101', 'Huancavelica', 'Huancavelica', 'Red de Salud Huancavelica', 3676, -12.7861, -74.9764, 4120, 22.5),
    ('090102', 'Huancavelica', 'Acobambilla', 'Red de Salud Huancavelica', 3795, -12.6542, -75.2819, 390, 84.0),
    ('090103', 'Huancavelica', 'Acoria', 'Red de Salud Huancavelica', 3167, -12.6378, -74.8614, 2450, 78.4),
    ('090108', 'Huancavelica', 'Huando', 'Red de Salud Huancavelica', 3562, -12.5625, -74.9453, 810, 76.2),
    ('090116', 'Huancavelica', 'Yauli', 'Red de Salud Huancavelica', 3391, -12.7697, -74.8511, 3150, 81.5),
    -- 2. Provincia de Acobamba
    ('090201', 'Acobamba', 'Acobamba', 'Red de Salud Acobamba', 3423, -12.8419, -74.5694, 1180, 48.0),
    ('090202', 'Acobamba', 'Andabamba', 'Red de Salud Acobamba', 3460, -12.7483, -74.6214, 520, 88.5),
    ('090206', 'Acobamba', 'Paucará', 'Red de Salud Acobamba', 3806, -12.7239, -74.6711, 2290, 82.1),
    ('090208', 'Acobamba', 'Rosario', 'Red de Salud Acobamba', 3640, -12.7686, -74.6142, 740, 86.4),
    -- 3. Provincia de Angaraes
    ('090301', 'Angaraes', 'Lircay', 'Red de Salud Angaraes', 3278, -12.9894, -74.7208, 2890, 56.3),
    ('090302', 'Angaraes', 'Anchonga', 'Red de Salud Angaraes', 3298, -12.9369, -74.7450, 860, 87.2),
    ('090304', 'Angaraes', 'Ccochaccasa', 'Red de Salud Angaraes', 4150, -12.9278, -74.7981, 380, 79.0),
    ('090311', 'Angaraes', 'Secclla', 'Red de Salud Angaraes', 3340, -13.0956, -74.5819, 410, 85.1),
    -- 4. Provincia de Castrovirreyna
    ('090401', 'Castrovirreyna', 'Castrovirreyna', 'Red de Salud Castrovirreyna', 3956, -13.2806, -75.3183, 390, 62.0),
    ('090409', 'Castrovirreyna', 'Huachos', 'Red de Salud Castrovirreyna', 2737, -13.2325, -75.5347, 190, 77.5),
    ('090411', 'Castrovirreyna', 'Santa Ana', 'Red de Salud Castrovirreyna', 4473, -13.0681, -75.1419, 210, 91.0),
    -- 5. Provincia de Churcampa
    ('090501', 'Churcampa', 'Churcampa', 'Red de Salud Churcampa', 3262, -12.7258, -74.3881, 640, 58.0),
    ('090502', 'Churcampa', 'Anco', 'Red de Salud Churcampa', 2404, -12.6331, -74.5875, 1020, 86.0),
    ('090508', 'Churcampa', 'Paucarbamba', 'Red de Salud Churcampa', 3370, -12.5594, -74.5361, 690, 84.5),
    ('090510', 'Churcampa', 'San Pedro de Coris', 'Red de Salud Churcampa', 3580, -12.5681, -74.4056, 430, 82.0),
    -- 6. Provincia de Huaytará
    ('090601', 'Huaytará', 'Huaytará', 'Red de Salud Huaytará', 2658, -13.6042, -75.3531, 260, 54.0),
    ('090606', 'Huaytará', 'Pilpichaca', 'Red de Salud Huaytará', 4092, -13.3328, -75.0169, 440, 92.3),
    ('090612', 'Huaytará', 'Santiago de Chocorvos', 'Red de Salud Huaytará', 2570, -13.8286, -75.2758, 310, 88.0),
    -- 7. Provincia de Tayacaja
    ('090701', 'Tayacaja', 'Pampas', 'Red de Salud Tayacaja', 3276, -12.3986, -74.8689, 1340, 44.5),
    ('090702', 'Tayacaja', 'Acostambo', 'Red de Salud Tayacaja', 3597, -12.3611, -75.0542, 470, 81.0),
    ('090704', 'Tayacaja', 'Colcabamba', 'Red de Salud Tayacaja', 2979, -12.4119, -74.6775, 2150, 83.4),
    ('090707', 'Tayacaja', 'Huachocolpa', 'Red de Salud Tayacaja', 2907, -12.1592, -74.5944, 580, 89.2),
    ('090715', 'Tayacaja', 'Surcubamba', 'Red de Salud Tayacaja', 2585, -12.1219, -74.6292, 610, 90.5)
ON CONFLICT (ubigeo) DO NOTHING;

