(function () {
  const pages = [
    ["/dashboard", "Dashboard"],
    ["/", "Consultar"],
    ["/lotes", "Carga masiva"],
    ["/legajos", "Legajos"],
    ["/configuracion", "Config."],
  ];
  const opsPages = [
    ["/padrones", "Padrones"],
    ["/fuentes", "Fuentes"],
    ["/fuentes-pendientes", "Cola asistida"],
    ["/regimenes", "Regímenes"],
    ["/accesos", "Accesos"],
    ["/info", "Diagnóstico"],
  ];
  const descriptions = {
    "/dashboard": ["Dashboard ejecutivo", "Vista de piloto por rol, riesgo fiscal, cobertura operativa y próximos pasos."],
    "/": ["Control fiscal de proveedores", "Validación live ARCA, padrones provinciales, obligaciones potenciales y legajo fiscal exportable."],
    "/lotes": ["Validación masiva", "Carga Excel/CSV para revisar proveedores por lote y generar evidencia consolidada."],
    "/padrones": ["Administración de padrones", "Carga, previsualización, calidad, vigencia e indexación de padrones fiscales."],
    "/regimenes": ["Mapa de regímenes fiscales", "Catálogo operativo de obligaciones nacionales, provinciales y municipales."],
    "/fuentes": ["Monitor de fuentes oficiales", "Seguimiento de organismos, descargas, evidencia y disponibilidad."],
    "/fuentes-pendientes": ["Cola asistida", "Tareas que requieren credenciales, navegador, evidencia o intervención humana."],
    "/accesos": ["Accesos fiscales", "Gestión de permisos, exportaciones y responsables por CUIT agente."],
    "/legajos": ["Legajos fiscales", "Historial de validaciones, evidencias y reportes generados."],
    "/configuracion": ["Configuración guiada", "Checklist de cobertura fiscal, padrones, fuentes y accesos para dejar el piloto operativo."],
    "/info": ["Diagnóstico técnico", "Estado técnico de ARCA, Supabase, padrones y fuentes disponibles."],
  };
  function pathKey() {
    const p = window.location.pathname.replace(/\/$/, "") || "/";
    if (p.startsWith("/legajos/")) return "/legajos";
    return descriptions[p] ? p : "/";
  }
  function injectAppbar() {
    const current = pathKey();
    const nav = pages.map(([href, label]) => {
      const active = current === href || (href !== "/" && window.location.pathname.startsWith(href));
      return `<a href="${href}" class="${active ? "active" : ""}">${label}</a>`;
    }).join("");
    const opsActive = opsPages.some(([href]) => current === href || window.location.pathname.startsWith(href));
    const opsNav = `<details class="menter-nav-group" ${opsActive ? "open" : ""}><summary class="${opsActive ? "active" : ""}">Operación</summary><div>${opsPages.map(([href, label]) => `<a href="${href}">${label}</a>`).join("")}</div></details>`;
    const bar = document.createElement("header");
    bar.className = "menter-appbar";
    bar.innerHTML = `
      <div class="menter-appbar-inner">
        <a class="menter-brand" href="/" aria-label="Menter inicio">
          <img src="/static/assets/menter-logo-new.png" alt="Menter.io" />
          <div><div class="menter-brand-title">Menter Fiscal</div><div class="menter-brand-subtitle">Infraestructura para control tributario</div></div>
        </a>
        <nav class="menter-nav" aria-label="Navegación principal">${nav}${opsNav}</nav>
        <div class="menter-badge">MVP CCU · Supabase</div>
      </div>`;
    document.body.prepend(bar);
  }
  function injectHero() {
    const current = pathKey();
    const [title, desc] = descriptions[current] || descriptions["/"];
    const hero = document.createElement("div");
    hero.className = "menter-page-hero";
    hero.innerHTML = `<div class="menter-page-hero-card"><div class="menter-eyebrow">Menter.io · Fiscal Ops</div><div class="menter-page-title">${title}</div><p class="menter-page-desc">${desc}</p></div>`;
    const main = document.querySelector("main");
    if (main) main.before(hero);
  }
  document.addEventListener("DOMContentLoaded", () => {
    injectAppbar();
    injectHero();
  });
})();
