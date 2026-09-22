/* Carga la especificación OpenAPI y renderiza la documentación. */

const HTTP_METHODS = ["get", "post", "put", "patch", "delete"];

const state = {
  spec: null,
  sections: [],
  activeSection: null,
};

const elements = {
  title: document.getElementById("doc-title"),
  version: document.getElementById("doc-version"),
  menu: document.getElementById("menu"),
  content: document.getElementById("content"),
  sidebar: document.getElementById("sidebar"),
  hamburger: document.getElementById("btn-menu"),
};

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = String(value ?? "");
  return div.innerHTML;
}

function resolveRef(schema, spec) {
  if (!schema || typeof schema !== "object") return schema;
  if (schema.$ref) {
    const name = schema.$ref.split("/").pop();
    const resolved = spec.components?.schemas?.[name];
    return resolved ? { ...resolved, $refName: name } : schema;
  }
  return schema;
}

function resolveType(schema, spec) {
  const resolved = resolveRef(schema, spec);
  if (resolved === null || typeof resolved !== "object") return "object";
  if (resolved.$refName) return resolved.$refName;
  if (resolved.type === "array") {
    const items = resolveRef(resolved.items, spec);
    return `array<${items?.type ?? items?.$refName ?? "unknown"}>`;
  }
  if (resolved.enum) {
    return `${resolved.type || "string"} (${resolved.enum.join(" | ")})`;
  }
  return resolved.type || "object";
}

function formatSchema(schema, spec) {
  const resolved = resolveRef(schema, spec);
  if (resolved === null || typeof resolved !== "object") return "<em>sin cuerpo</em>";

  if (resolved.type === "array") {
    const items = resolveRef(resolved.items, spec);
    if (items && items.properties) {
      return renderSchemaFields(items, spec);
    }
    return `<code>${escapeHtml(resolveType(schema, spec))}</code>`;
  }

  if (resolved.properties) {
    return renderSchemaFields(resolved, spec);
  }

  return `<code>${escapeHtml(resolveType(schema, spec))}</code>`;
}

function renderSchemaFields(schema, spec) {
  const required = schema.required || [];
  const props = schema.properties || {};

  const rows = Object.entries(props)
    .map(([name, propSchema]) => {
      const resolved = resolveRef(propSchema, spec);
      const isRequired = required.includes(name);
      const type = resolveType(propSchema, spec);
      const description = resolved.description ? ` - ${resolved.description}` : "";
      return (
        `<tr>` +
        `<td><code>${escapeHtml(name)}</code>` +
        (isRequired ? `<span class="badge badge-required">requerido</span>` : "") +
        `</td>` +
        `<td><code>${escapeHtml(type)}</code></td>` +
        `<td>${escapeHtml(description)}</td>` +
        `</tr>`
      );
    })
    .join("");

  return (
    `<table class="param-table">` +
    `<thead><tr><th>Campo</th><th>Tipo</th><th>Descripción</th></tr></thead>` +
    `<tbody>${rows}</tbody>` +
    `</table>`
  );
}

function renderParameters(parameters, spec) {
  if (!parameters || parameters.length === 0) return "";
  const rows = parameters
    .map((param) => {
      const required = param.required ? `<span class="required-true">sí</span>` : "no";
      const type = param.schema ? resolveType(param.schema, spec) : "string";
      const description = param.description ? ` - ${param.description}` : "";
      return (
        `<tr>` +
        `<td><code>${escapeHtml(param.name)}</code> <span class="badge">${escapeHtml(param.in)}</span></td>` +
        `<td><code>${escapeHtml(type)}</code></td>` +
        `<td>${required}</td>` +
        `<td>${escapeHtml(description)}</td>` +
        `</tr>`
      );
    })
    .join("");

  return (
    `<h3>Parámetros</h3>` +
    `<table class="param-table">` +
    `<thead><tr><th>Nombre</th><th>Tipo</th><th>Requerido</th><th>Descripción</th></tr></thead>` +
    `<tbody>${rows}</tbody>` +
    `</table>`
  );
}

function renderRequestBody(operation, spec) {
  const content = operation.requestBody?.content;
  if (!content) return "";
  const media = content["application/json"] || content["application/x-www-form-urlencoded"];
  if (!media?.schema) return "";

  const label =
    content["application/json"] ? "application/json" : Object.keys(content)[0];
  return (
    `<h3>Request body (${escapeHtml(label)})</h3>` +
    formatSchema(media.schema, spec)
  );
}

function renderResponses(operation) {
  const responses = operation.responses || {};
  const rows = Object.entries(responses)
    .map(([code, response]) => {
      return (
        `<tr><td><code>${escapeHtml(code)}</code></td>` +
        `<td>${escapeHtml(response.description)}</td></tr>`
      );
    })
    .join("");

  return (
    `<h3>Respuestas</h3>` +
    `<table class="param-table">` +
    `<thead><tr><th>Código</th><th>Descripción</th></tr></thead>` +
    `<tbody>${rows}</tbody>` +
    `</table>`
  );
}

function renderEndpoint(path, item, method, operation, spec) {
  const summary = operation.summary
    ? `<div class="endpoint-summary">${escapeHtml(operation.summary)}</div>`
    : "";
  const description = operation.description
    ? `<div class="endpoint-description">${escapeHtml(operation.description)}</div>`
    : "";

  return (
    `<div class="endpoint">` +
    `<div class="endpoint-head">` +
    `<span class="method method-${method.toUpperCase()}">${method.toUpperCase()}</span>` +
    `<code class="endpoint-path">${escapeHtml(path)}</code>` +
    `</div>` +
    summary +
    description +
    renderParameters(operation.parameters, spec) +
    renderRequestBody(operation, spec) +
    renderResponses(operation) +
    `</div>`
  );
}

function renderOverview(spec) {
  const description = spec.info?.description
    ? `<p>${escapeHtml(spec.info.description)}</p>`
    : "";
  return (
    `<h2>${escapeHtml(spec.info?.title || "API")}</h2>` +
    description +
    `<h3>Secciones disponibles</h3>` +
    `<p>Selecciona una sección en el menú lateral para ver sus endpoints.</p>`
  );
}

function renderSection(section, spec) {
  const endpoints = Object.entries(spec.paths)
    .filter(([, item]) => {
      const method = HTTP_METHODS.find((m) => item[m]);
      const tags = method ? item[method].tags : [];
      return tags.includes(section.id);
    })
    .map(([path, item]) => {
      return HTTP_METHODS.filter((method) => item[method])
        .map((method) => {
          return renderEndpoint(path, item, method, item[method], spec);
        })
        .join("");
    })
    .join("");

  return `<h2>${escapeHtml(section.label)}</h2>${endpoints}`;
}

function setActive(sectionId) {
  state.activeSection = sectionId;
  document.querySelectorAll(".menu li").forEach((li) => {
    li.classList.toggle("active", li.dataset.section === sectionId);
  });
  closeSidebar();
}

function buildMenu(spec) {
  elements.menu.innerHTML = "";

  const overview = document.createElement("li");
  overview.dataset.section = "__overview__";
  overview.textContent = "Inicio";
  overview.addEventListener("click", () => {
    setActive("__overview__");
    elements.content.innerHTML = renderOverview(spec);
  });
  elements.menu.appendChild(overview);

  state.sections.forEach((section) => {
    const li = document.createElement("li");
    li.dataset.section = section.id;
    li.textContent = section.label;
    li.addEventListener("click", () => {
      setActive(section.id);
      elements.content.innerHTML = renderSection(section, spec);
    });
    elements.menu.appendChild(li);
  });

  elements.menu.firstElementChild.click();
}

function buildSections(spec) {
  const seen = new Set();
  const sections = [];

  Object.values(spec.paths).forEach((item) => {
    const method = HTTP_METHODS.find((m) => item[m]);
    const tags = method ? item[method].tags : [];
    if (Array.isArray(tags)) {
      tags.forEach((tag) => {
        if (!seen.has(tag)) {
          seen.add(tag);
          sections.push({ id: tag, label: capitalize(tag) });
        }
      });
    }
  });

  return sections;
}

function capitalize(value) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function closeSidebar() {
  elements.sidebar.classList.remove("open");
  elements.hamburger.setAttribute("aria-expanded", "false");
}

elements.hamburger.addEventListener("click", () => {
  const open = elements.sidebar.classList.toggle("open");
  elements.hamburger.setAttribute("aria-expanded", String(open));
});

fetch("/openapi.json")
  .then((response) => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then((spec) => {
    state.spec = spec;
    elements.title.textContent = spec.info?.title || "API";
    elements.version.textContent = spec.info?.version
      ? `v${spec.info.version}`
      : "";
    state.sections = buildSections(spec);
    buildMenu(spec);
  })
  .catch((error) => {
    elements.content.innerHTML =
      `<h2>No se pudo cargar la documentación</h2>` +
      `<p>${escapeHtml(error.message)}</p>`;
  });
