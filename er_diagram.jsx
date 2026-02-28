import { useState } from "react";

const TABLES = {
  Cases: {
    color: "#C8A96E",
    accent: "#F5DFA0",
    x: 320,
    y: 60,
    pk: "id (PK)",
    fields: [
      { name: "record_number", type: "INT UNIQUE", note: "DAIL ID" },
      { name: "caption", type: "NVARCHAR(255)" },
      { name: "case_snug", type: "NVARCHAR(255)" },
      { name: "brief_description", type: "NVARCHAR(MAX)" },
      { name: "area_of_application", type: "NVARCHAR(255)" },
      { name: "issue_text", type: "NVARCHAR(MAX)" },
      { name: "cause_of_action", type: "NVARCHAR(255)" },
      { name: "algorithm_name", type: "NVARCHAR(255)" },
      { name: "is_class_action", type: "BIT" },
      { name: "organizations_involved", type: "NVARCHAR(255)" },
      { name: "jurisdiction_filed", type: "NVARCHAR(255)" },
      { name: "date_action_filed", type: "DATE" },
      { name: "jurisdiction_type", type: "NVARCHAR(255)" },
      { name: "jurisdiction_name", type: "NVARCHAR(255)" },
      { name: "status_disposition", type: "NVARCHAR(255)" },
      { name: "has_published_opinion", type: "BIT" },
      { name: "date_added", type: "DATETIME2" },
      { name: "last_update", type: "DATETIME2" },
      { name: "most_recent_activity", type: "NVARCHAR(255)" },
      { name: "most_recent_activity_date", type: "DATE" },
      { name: "researcher", type: "NVARCHAR(255)" },
      { name: "summary_of_significance", type: "NVARCHAR(MAX)" },
      { name: "summary_facts", type: "NVARCHAR(MAX)" },
      { name: "keyword", type: "NVARCHAR(255)" },
    ],
  },
  Dockets: {
    color: "#6E9EC8",
    accent: "#A0C8F5",
    x: 30,
    y: 320,
    pk: "id (PK)",
    fields: [
      { name: "case_number", type: "INT", note: "FK → Cases.record_number" },
      { name: "court", type: "NVARCHAR(MAX)" },
      { name: "docket_number", type: "NVARCHAR(255)" },
      { name: "link", type: "NVARCHAR(MAX)", note: "CourtListener URL" },
    ],
  },
  Documents: {
    color: "#6EC88A",
    accent: "#A0F5B8",
    x: 320,
    y: 620,
    pk: "id (PK)",
    fields: [
      { name: "case_number", type: "INT", note: "FK → Cases.record_number" },
      { name: "court", type: "NVARCHAR(255)" },
      { name: "document_date", type: "DATE" },
      { name: "link", type: "NVARCHAR(MAX)", note: "RECAP PDF URL" },
      { name: "cite_or_reference", type: "NVARCHAR(255)", note: "Westlaw/LEXIS" },
      { name: "document_title", type: "NVARCHAR(MAX)" },
    ],
  },
  SecondarySources: {
    color: "#C86E9E",
    accent: "#F5A0CC",
    x: 620,
    y: 320,
    pk: "id (PK)",
    fields: [
      { name: "case_number", type: "INT", note: "FK → Cases.record_number" },
      { name: "secondary_source_link", type: "NVARCHAR(MAX)" },
      { name: "secondary_source_title", type: "NVARCHAR(MAX)" },
    ],
  },
  CourtListenerSync: {
    color: "#9E6EC8",
    accent: "#CCA0F5",
    x: 620,
    y: 580,
    pk: "id (PK)",
    fields: [
      { name: "case_number", type: "INT", note: "FK → Cases.record_number" },
      { name: "docket_id", type: "NVARCHAR(255)" },
      { name: "synced_at", type: "DATETIME2" },
      { name: "status", type: "NVARCHAR(50)", note: "success|error|partial" },
      { name: "records_fetched", type: "INT" },
      { name: "error_message", type: "NVARCHAR(MAX)" },
    ],
  },
};

const TABLE_W = 260;
const ROW_H = 22;
const HEADER_H = 52;

function getTableHeight(t) {
  return HEADER_H + ROW_H + (t.fields.length * ROW_H) + 8;
}

// Connection midpoints for each FK table to Cases center-bottom/sides
const CONNECTIONS = [
  { from: "Dockets", to: "Cases", label: "case_number → record_number", cardinality: "N:1" },
  { from: "Documents", to: "Cases", label: "case_number → record_number", cardinality: "N:1" },
  { from: "SecondarySources", to: "Cases", label: "case_number → record_number", cardinality: "N:1" },
  { from: "CourtListenerSync", to: "Cases", label: "case_number → record_number", cardinality: "N:1" },
];

function getConnectorPoints(fromName, toName) {
  const from = TABLES[fromName];
  const to = TABLES[toName];
  const fh = getTableHeight(from);
  const th = getTableHeight(to);

  const fx = from.x + TABLE_W / 2;
  const fy = from.y + fh / 2;
  const tx = to.x + TABLE_W / 2;
  const ty = to.y + th / 2;

  // Pick edges based on relative position
  let x1, y1, x2, y2;

  if (fromName === "Dockets") {
    x1 = from.x + TABLE_W; y1 = from.y + fh / 2;
    x2 = to.x; y2 = to.y + th / 2;
  } else if (fromName === "Documents") {
    x1 = from.x + TABLE_W / 2; y1 = from.y;
    x2 = to.x + TABLE_W / 2; y2 = to.y + th;
  } else if (fromName === "SecondarySources") {
    x1 = from.x; y1 = from.y + fh / 2;
    x2 = to.x + TABLE_W; y2 = to.y + th / 2;
  } else if (fromName === "CourtListenerSync") {
    x1 = from.x; y1 = from.y + fh * 0.3;
    x2 = to.x + TABLE_W; y2 = to.y + th * 0.75;
  }

  const mx = (x1 + x2) / 2;
  const my = (y1 + y2) / 2;
  return { x1, y1, x2, y2, mx, my };
}

function TableCard({ name, table, isHighlighted, onHover }) {
  const h = getTableHeight(table);
  return (
    <g
      transform={`translate(${table.x}, ${table.y})`}
      onMouseEnter={() => onHover(name)}
      onMouseLeave={() => onHover(null)}
      style={{ cursor: "pointer" }}
    >
      {/* Shadow */}
      <rect x={4} y={4} width={TABLE_W} height={h} rx={8} fill="rgba(0,0,0,0.35)" />
      {/* Body */}
      <rect
        width={TABLE_W}
        height={h}
        rx={8}
        fill="#1A1D26"
        stroke={isHighlighted ? table.color : "#2E3144"}
        strokeWidth={isHighlighted ? 2.5 : 1.5}
      />
      {/* Header */}
      <rect width={TABLE_W} height={HEADER_H} rx={8} fill={table.color} opacity={0.9} />
      <rect y={HEADER_H - 8} width={TABLE_W} height={8} fill={table.color} opacity={0.9} />

      {/* Table name */}
      <text x={TABLE_W / 2} y={22} textAnchor="middle" fill="#0A0C14"
        style={{ fontFamily: "'Courier Prime', monospace", fontWeight: "700", fontSize: 13 }}>
        {name}
      </text>

      {/* PK */}
      <rect x={8} y={30} width={TABLE_W - 16} height={18} rx={3}
        fill="rgba(0,0,0,0.25)" />
      <text x={16} y={43} fill={table.accent}
        style={{ fontFamily: "'Courier Prime', monospace", fontSize: 10.5, fontWeight: "700" }}>
        🔑 {table.pk}
      </text>

      {/* Divider */}
      <line x1={0} y1={HEADER_H} x2={TABLE_W} y2={HEADER_H} stroke="#2E3144" strokeWidth={1} />

      {/* Fields */}
      {table.fields.map((f, i) => (
        <g key={f.name} transform={`translate(0, ${HEADER_H + 4 + i * ROW_H})`}>
          {i % 2 === 0 && (
            <rect x={0} width={TABLE_W} height={ROW_H} fill="rgba(255,255,255,0.03)" />
          )}
          {f.name.includes("_number") || f.name === "case_number" ? (
            <text x={10} y={15} fill="#7B8CDE"
              style={{ fontFamily: "'Courier Prime', monospace", fontSize: 9.5 }}>
              🔗
            </text>
          ) : null}
          <text x={f.name.includes("_number") ? 22 : 10} y={15}
            fill={f.note ? table.accent : "#8B93B0"}
            style={{ fontFamily: "'Courier Prime', monospace", fontSize: 9.5 }}>
            {f.name}
          </text>
          <text x={TABLE_W - 8} y={15} textAnchor="end" fill="#4A5068"
            style={{ fontFamily: "'Courier Prime', monospace", fontSize: 8.5 }}>
            {f.type}
          </text>
        </g>
      ))}
    </g>
  );
}

export default function ERDiagram() {
  const [hovered, setHovered] = useState(null);

  const svgW = 940;
  const svgH = 870;

  return (
    <div style={{
      background: "linear-gradient(135deg, #0A0C14 0%, #0F1220 50%, #0A0C14 100%)",
      minHeight: "100vh",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      padding: "24px 16px",
      fontFamily: "'Courier Prime', monospace",
    }}>
      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: 24, maxWidth: 700 }}>
        <div style={{ color: "#C8A96E", fontSize: 11, letterSpacing: 4, marginBottom: 6 }}>
          DATABASE SCHEMA
        </div>
        <h1 style={{
          color: "#E8E0D0",
          fontSize: 26,
          fontWeight: 700,
          margin: "0 0 8px",
          letterSpacing: 1,
        }}>
          DAIL · Entity Relationship Diagram
        </h1>
        <p style={{ color: "#5A6080", fontSize: 12, margin: 0 }}>
          Database of AI Litigation · SQL Server · Hover a table to highlight its connections
        </p>
      </div>

      {/* Legend */}
      <div style={{ display: "flex", gap: 20, marginBottom: 20, flexWrap: "wrap", justifyContent: "center" }}>
        {Object.entries(TABLES).map(([name, t]) => (
          <div key={name} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <div style={{ width: 10, height: 10, borderRadius: 2, background: t.color }} />
            <span style={{ color: "#8B93B0", fontSize: 11 }}>{name}</span>
          </div>
        ))}
      </div>

      {/* SVG ER Diagram */}
      <div style={{
        background: "#0D0F1A",
        border: "1px solid #1E2235",
        borderRadius: 12,
        padding: 8,
        boxShadow: "0 20px 60px rgba(0,0,0,0.6)",
        overflow: "auto",
        maxWidth: "100%",
      }}>
        <svg width={svgW} height={svgH} viewBox={`0 0 ${svgW} ${svgH}`}>
          <defs>
            <marker id="arrowFK" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
              <path d="M0,0 L0,6 L8,3 z" fill="#4A5068" />
            </marker>
            <marker id="arrowFKHover" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
              <path d="M0,0 L0,6 L8,3 z" fill="#C8A96E" />
            </marker>
          </defs>

          {/* Grid dots */}
          {Array.from({ length: 30 }).map((_, i) =>
            Array.from({ length: 20 }).map((__, j) => (
              <circle key={`${i}-${j}`} cx={i * 32} cy={j * 44} r={0.8} fill="#1A1D26" />
            ))
          )}

          {/* Connections */}
          {CONNECTIONS.map((conn) => {
            const { x1, y1, x2, y2, mx, my } = getConnectorPoints(conn.from, conn.to);
            const isActive = hovered === conn.from || hovered === conn.to || hovered === null;
            const color = (hovered === conn.from || hovered === conn.to)
              ? TABLES[conn.from].color : "#2E3550";
            const strokeW = (hovered === conn.from || hovered === conn.to) ? 2 : 1.2;

            return (
              <g key={conn.from} opacity={isActive ? 1 : 0.2}>
                <path
                  d={`M${x1},${y1} C${mx},${y1} ${mx},${y2} ${x2},${y2}`}
                  fill="none"
                  stroke={color}
                  strokeWidth={strokeW}
                  strokeDasharray={hovered ? "none" : "5,3"}
                  markerEnd={`url(#arrowFK)`}
                />
                {/* Cardinality label */}
                <rect x={mx - 16} y={my - 10} width={32} height={14} rx={3}
                  fill="#0D0F1A" stroke={color} strokeWidth={0.8} />
                <text x={mx} y={my} textAnchor="middle" fill={color}
                  style={{ fontSize: 8.5, fontFamily: "monospace" }}>
                  {conn.cardinality}
                </text>
              </g>
            );
          })}

          {/* Tables */}
          {Object.entries(TABLES).map(([name, table]) => (
            <TableCard
              key={name}
              name={name}
              table={table}
              isHighlighted={hovered === name}
              onHover={setHovered}
            />
          ))}
        </svg>
      </div>

      {/* API Endpoints Reference */}
      <div style={{
        marginTop: 28,
        width: "100%",
        maxWidth: 900,
        background: "#0D0F1A",
        border: "1px solid #1E2235",
        borderRadius: 12,
        padding: "20px 24px",
      }}>
        <div style={{ color: "#C8A96E", fontSize: 10, letterSpacing: 3, marginBottom: 14 }}>
          REST API ENDPOINTS
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
          {[
            ["GET", "/cases", "Search & filter cases", "#6E9EC8"],
            ["GET", "/cases/{id}", "Full case detail + related data", "#6E9EC8"],
            ["GET", "/cases/{id}/docket", "Court docket info", "#6EC88A"],
            ["GET", "/cases/{id}/documents", "All case documents", "#6EC88A"],
            ["GET", "/documents", "Search documents across cases", "#6EC88A"],
            ["GET", "/cases/{id}/secondary-sources", "Articles & press coverage", "#C86E9E"],
            ["GET", "/secondary-sources", "Search all secondary sources", "#C86E9E"],
            ["GET", "/analytics/summary", "DB-wide stats & breakdowns", "#9E6EC8"],
          ].map(([method, path, desc, color]) => (
            <div key={path} style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              padding: "7px 10px",
              background: "#141620",
              borderRadius: 6,
              borderLeft: `3px solid ${color}`,
            }}>
              <span style={{
                color,
                fontSize: 9,
                fontWeight: 700,
                letterSpacing: 1,
                minWidth: 32,
              }}>{method}</span>
              <span style={{ color: "#E8E0D0", fontSize: 10, flex: 1 }}>{path}</span>
              <span style={{ color: "#4A5068", fontSize: 9 }}>{desc}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
