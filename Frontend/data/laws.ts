// Mock data for Veeduría Congreso Colombia

export interface VotingStats {
  favor: number;
  contra: number;
  abstenciones: number;
  total: number;
}

export interface Law {
  id: string;
  titulo: string;
  descripcion: string;
  estado: string;
  estadoColor: string;
  autor: string;
  partido: string;
  partidoColor: string;
  fechaRadicacion: string;
  votacion: VotingStats;
  chatHistory: { role: "user" | "ia"; texto: string }[];
}

const laws: Law[] = [
  {
    id: "pl-043-2024",
    titulo: "Proyecto de Ley 043 – Reforma a la Salud",
    descripcion:
      "Reforma estructural del sistema de salud colombiano. Elimina las EPS como intermediarias y transfiere los recursos directamente a las clínicas y hospitales públicos.",
    estado: "En segundo debate",
    estadoColor: "amber",
    autor: "Sen. Francia Márquez Mina",
    partido: "Pacto Histórico",
    partidoColor: "purple",
    fechaRadicacion: "2024-03-10",
    votacion: { favor: 54, contra: 47, abstenciones: 8, total: 109 },
    chatHistory: [
      {
        role: "user",
        texto: "¿Qué implica eliminar las EPS en la práctica?",
      },
      {
        role: "ia",
        texto:
          "Si se eliminan las EPS, los recursos del sistema pasarían directamente a los hospitales y clínicas. Esto busca reducir la intermediación financiera, pero algunos expertos advierten riesgos en la transición por la capacidad operativa del Estado.",
      },
      {
        role: "user",
        texto: "¿Cuándo entraría en vigor si se aprueba?",
      },
      {
        role: "ia",
        texto:
          "Según el texto actual, la implementación sería gradual: 18 meses para zona urbana y 24 meses para zonas rurales y dispersas desde la promulgación de la ley.",
      },
    ],
  },
  {
    id: "pl-127-2024",
    titulo: "Proyecto de Ley 127 – Licencia de Paternidad Ampliada",
    descripcion:
      "Amplía la licencia de paternidad de 2 semanas a 8 semanas pagas, equiparándola progresivamente a la licencia de maternidad para promover la corresponsabilidad en el hogar.",
    estado: "Aprobada",
    estadoColor: "green",
    autor: "Sen. Ariel Ávila Martínez",
    partido: "Colombia Humana",
    partidoColor: "red",
    fechaRadicacion: "2024-01-22",
    votacion: { favor: 89, contra: 12, abstenciones: 5, total: 106 },
    chatHistory: [
      {
        role: "user",
        texto: "¿Quiénes se benefician de esta ley?",
      },
      {
        role: "ia",
        texto:
          "Todos los padres trabajadores con contrato laboral formal en Colombia. La ley aplica tanto al sector privado como al público y cubre también a parejas del mismo sexo.",
      },
    ],
  },
  {
    id: "pl-208-2024",
    titulo: "Proyecto de Ley 208 – Cadena Perpetua para Femicidas",
    descripcion:
      "Propone modificar el Código Penal para establecer pena de prisión perpetua revisable (mínimo 25 años) para personas condenadas por feminicidio agravado.",
    estado: "En primer debate",
    estadoColor: "blue",
    autor: "Sen. Paloma Valencia Laserna",
    partido: "Centro Democrático",
    partidoColor: "orange",
    fechaRadicacion: "2024-05-08",
    votacion: { favor: 61, contra: 39, abstenciones: 12, total: 112 },
    chatHistory: [
      {
        role: "user",
        texto: "¿Es constitucional la cadena perpetua en Colombia?",
      },
      {
        role: "ia",
        texto:
          "Es un debate activo. En 2021, el Congreso aprobó un acto legislativo que permitió la cadena perpetua para violadores y asesinos de niños, pero la Corte Constitucional lo declaró inexequible. Esta nueva propuesta intenta un articulado diferente para superar ese fallo.",
      },
      {
        role: "user",
        texto: "¿Cuántos votos necesita para pasar a segundo debate?",
      },
      {
        role: "ia",
        texto:
          "Necesita mayoría simple (la mitad más uno de los miembros presentes) en la comisión primera del Senado para avanzar al segundo debate en plenaria.",
      },
    ],
  },
  {
    id: "pl-315-2024",
    titulo: "Proyecto de Ley 315 – Internet como Derecho Fundamental",
    descripcion:
      "Declara el acceso a internet como derecho fundamental, obliga al Estado a garantizar conectividad básica gratuita en zonas rurales y crea el Fondo Nacional de Inclusión Digital.",
    estado: "Archivado",
    estadoColor: "gray",
    autor: "Rep. David Racero Mayorca",
    partido: "Pacto Histórico",
    partidoColor: "purple",
    fechaRadicacion: "2023-11-14",
    votacion: { favor: 38, contra: 62, abstenciones: 9, total: 109 },
    chatHistory: [
      {
        role: "user",
        texto: "¿Por qué fue archivado este proyecto?",
      },
      {
        role: "ia",
        texto:
          "El proyecto fue archivado al término de la legislatura sin haber sido debatido en plenaria. Según el reglamento del Congreso, los proyectos que no avanzan en dos legislaturas consecutivas se archivan automáticamente.",
      },
    ],
  },
];

export default laws;
