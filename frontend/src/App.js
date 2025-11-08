import React, { useState, useEffect, useRef } from 'react';
import axios from "axios";
import { Box, Card, CardContent, Typography, Grid, List, ListItem } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import { teal, grey } from '@mui/material/colors';
import useLatestUsageCO2 from './hooks/useLatestUsageCO2';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';

function FitBounds({ markers }) {
  const map = useMap();
  useEffect(() => {
    if (!map || !markers.length) return;
    const bounds = markers.map(m => [m.lat, m.lon]);
    if(bounds.length === 1) {
      map.setView(bounds[0], 13);
    } else if(bounds.length > 1) {
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [markers, map]);
  return null;
}

function extractBauteilMarkersFromCF(submodel) {
  if (!submodel?.submodelElements) return [];
  const outerCol = submodel.submodelElements.find(e => e.idShort === "BauteilAdressen");
  if (!outerCol?.value) return [];
  const innerCol = outerCol.value.find(e => e.idShort === "BauteilAdressen");
  if (!innerCol?.value) return [];
  return innerCol.value.map((part, i) => {
    const get = idShort => (part.value || []).find(e => e.idShort === idShort);
    const lat = parseFloat(get("Latitude")?.value ?? "");
    const lon = parseFloat(get("Longitude")?.value ?? "");
    if (isNaN(lat) || isNaN(lon)) return null;
    return {
      name: get("Name")?.value || part.idShort,
      address: [
        get("Street")?.value,
        get("HouseNumber")?.value,
        get("ZipCode")?.value,
        get("CityTown")?.value,
        get("Country")?.value
      ].filter(Boolean).join(", "),
      lat, lon
    }
  }).filter(Boolean);
}

// Datasheet Kategorien
const CATEGORY_MAPPING = {
  motor: "Motors",
  netzteil: "Power Supplies",
  iolink: "IO-Links",
  geraet: "Devices",
  sensor: "Sensors",
  relais: "Relays and Relay Sockets",
  leuchte: "Signal Light",
  encoder: "Encoder",
  sicherung: "Fuses",
  router: "Router",
};

function resolveCategory(name) {
  const n = name.toLowerCase();
  if(n.includes("io-link") || n.includes("jxcl18-ley16b-100")) return "iolink";
  if(n.includes("motor")) return "motor";
  if(n.includes("ley16") || n.includes("leyg16")) return "motor";
  if(n.includes("netzteil") || n.includes("315-00011") || n.includes("power")) return "netzteil";
  if(n.includes("simatic") || n.includes("gerät") || n.includes("sig") || n.includes("sim") || n.includes("cpu")) return "geraet";
  if(n.includes("sensor") || n.includes("we4")) return "sensor";
  if(n.includes("finder")) return "relais";
  if(n.includes("werma")) return "leuchte";
  if(n.includes("encoder") || n.includes("ahm36")) return "encoder";
  if(n.includes("sicherung") || n.includes("littelfuse")) return "sicherung";
  if(n.includes("tp-link") || n.includes("router")) return "router";
  return "Sonstige";
}

const svgString = encodeURIComponent(
  `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32">
    <circle cx="16" cy="16" r="10" fill="#0078FF" stroke="#fff" stroke-width="3"/>
  </svg>`
);
const svgUrl = `data:image/svg+xml,${svgString}`;

const svgIcon = new L.Icon({
  iconUrl: svgUrl,
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32]
});

function useDpp(productPassId) {
  const [data, setData] = React.useState(null);
  React.useEffect(() => {
    if (!productPassId) return;
    axios.get('http://localhost:8000/product_pass/' + productPassId)
      .then(r => setData(r.data))
      .catch(() => setData(null));
  }, [productPassId]);
  return data;
}

function renderAddress(addressArray) {
  if (!Array.isArray(addressArray)) return null;
  return (
    <table style={{ borderCollapse: "collapse", marginTop: "8px", background: '#f7fafd' }}>
      <tbody>
        {addressArray.map(row =>
          <tr key={row.idShort || row.value}>
            <td style={{ padding: "2px 8px", fontWeight: 500, color:"#6D6D6D" }}>{row.idShort}:</td>
            <td style={{ padding: "2px 8px", color: "#333" }}>{row.value}</td>
          </tr>
        )}
      </tbody>
    </table>
  );
}
function getPdfUrlFromDatasheet(el) {
  if (!Array.isArray(el.value)) return null;
  const docVersion = el.value.find(e => e.idShort && e.idShort.startsWith("DocumentVersion"));
  if (!docVersion || !Array.isArray(docVersion.value)) return null;
  const fileObj = docVersion.value.find(e => e.modelType === "File" && e.value);
  if (!fileObj) return null;
  let fileUrl = fileObj.value;
  if (typeof fileUrl !== "string") return null;
  if (fileUrl.startsWith("http://") || fileUrl.startsWith("https://")) {
    return fileUrl;
  }
  if (fileUrl.startsWith("/")) fileUrl = fileUrl.substring(1);
  return "http://localhost:8000/" + fileUrl;
}

function AssetInfo({ shell }) {
  if (!shell) return null;
  let thumbnailPath = shell.assetInformation?.defaultThumbnail?.path;
  const fallbackImage = "https://ywheivlrppourvacbxkz.supabase.co/storage/v1/object/public/images//thumbnail_sortingmachine.jpg";
  if (!thumbnailPath || typeof thumbnailPath !== 'string' || !thumbnailPath.trim()) {
    thumbnailPath = fallbackImage.replace("http://localhost:8000/files/", "");
  } else if (thumbnailPath.startsWith("/")) {
    thumbnailPath = thumbnailPath.substring(1);
  }
  const thumbnailUrl = "http://localhost:8000/files/" + thumbnailPath;
  
  return (
  <Card sx={{ mb:2, position: "relative" }}>
    <CardContent sx={{ position: "relative" }}>
      <img
        src="https://ywheivlrppourvacbxkz.supabase.co/storage/v1/object/public/images//FHTW_Logo_Farbe_transparent.png"
        alt="FH Logo"
        width={180}
        style={{
          position: "absolute",
          top: 12,
          right: 24,
          zIndex: 10,
        }}
      />
      <Grid container spacing={2}>
        <Grid item xs={12} md={8}>
          <Typography variant="h6" gutterBottom>
            <b>Asset Administration Shell</b>
          </Typography>
          <div><b>id:</b> {shell.id}</div>
          <div><b>idShort:</b> {shell.idShort}</div>
          <div><b>Name(n):</b> {shell.displayName?.map(e => e.text).join(" / ")}</div>
        </Grid>
        <Grid item xs={12} md={4} style={{textAlign: "right"}}>
          <img
            src={thumbnailUrl}
            alt="Produkt"
            width={160}
            height="auto"
            style={{ borderRadius: 14, boxShadow: "0 1px 8px 0 #ccc" }}
            onError={e => { e.target.onerror = null; e.target.src = fallbackImage; }}
          /><br/>
        </Grid>
      </Grid>
    </CardContent>
  </Card>
);
}

function SubmodelSidebar({ submodels, selected, setSelected }) {
  return (
    <Box sx={{ borderRight: 1, borderColor: '#ddd', minWidth: 200, bgcolor: "#f7fafd" }}>
      <List>
        {submodels.map((sm, i) =>
          <ListItem button key={sm.idShort || sm.id || i}
            selected={selected === i}
            onClick={() => setSelected(i)}
          >
            <b>{sm.idShort || sm.id}</b>
          </ListItem>
        )}
      </List>
    </Box>
  );
}
const phases = [
  { key: "A1", label: "A1 - raw material supply (and upstream production)" },
  { key: "A2", label: "A2 - cradle-to-gate transport to factory" },
  { key: "A3", label: "A3 - production" },
  { key: "A4", label: "A4 - transport to final destination" },
  { key: "B1", label: "B1 - usage phase: not yet included" }
];

const COLOURS = ["#156b72", "#338c94", "#67b3ba", "#b6d2d9", "#bcbcbc"];

function StackedCO2Bar({ values }) {
  const data = [{
    name: "CO₂ Equivalents",
    A3: values.A3,
    A2: values.A2,
    A1: values.A1,
    ...(values.A4 > 0 ? { A4: values.A4 } : {}),
    B1: values.B1,
  }];

  const total = Object.values(values).reduce((sum, v) => sum + v, 0);

  return (
    <Box sx={{ width: "500px", minWidth: "500px", maxWidth: "1200px" }}>
      <Typography sx={{ fontSize: 14, color: "#000", fontWeight: 400, mb: 1 }}>
        CO₂ distribution
      </Typography>
      <Typography sx={{ fontSize: 40, fontWeight: 700, color: "#000" }}>
        {total.toFixed(3)} <span style={{ fontSize: 22, fontWeight: 400 }}>kg in total</span>
      </Typography>

      <div style={{ width: "500", minWidth: 500, height: 320 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 45, left: 40, bottom: 70 }}>
            
            {/* X-Achse */}
            <XAxis
              dataKey="name"
              axisLine={true}
              tick={true}
              label={{
                offset: 30,
                position: "Bottom",
                style: { fill: "#000", fontWeight: 300, fontSize: 14 }
              }}
            />

            {/* Y-Achse */}
            <YAxis
              domain={[0, total]}
              ticks={[
                0,
                Number((total * 0.33).toFixed(3)),
                Number((total * 0.66).toFixed(3)),
                Number(total.toFixed(3))
              ]}
              label={{
                value: 'kg CO₂',
                angle: -90,
                position: 'insideleft',
                dx: -35,
                style: { fill: "#000", fontWeight: 300, fontSize: 14 }
              }}
              tick={{ fill: "#000", fontWeight: 600, fontSize: 14 }}
              tickLine={{ stroke: "#000" }}
              axisLine={{ stroke: "#000" }}
            />

            {/* Tooltip */}
            <Tooltip formatter={(val) => `${val.toFixed(3)} kg`} labelFormatter={() => ""} />

            {/* Balken */}
            <Bar dataKey="A3" stackId="1" fill={COLOURS[0]} name="A3" />
            <Bar dataKey="A2" stackId="1" fill={COLOURS[1]} name="A2" />
            <Bar dataKey="A1" stackId="1" fill={COLOURS[2]} name="A1" />
            {values.A4 > 0 && (
              <Bar dataKey="A4" stackId="1" fill={COLOURS[3]} name="A4" />
            )}
            <Bar dataKey="B1" stackId="1" fill={COLOURS[4]} name="B1" />

            {/* Legende */}
            <Legend
              layout="horizontal"
              align="center"
              verticalAlign="bottom"
              iconType="square"
              wrapperStyle={{ paddingTop: 25 }}
              formatter={(value) => (
                <span style={{ color: "#000", fontWeight: 700, fontSize: 18 }}>{value}</span>
              )}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Box>
  );
}

function CarbonFootprintSummary({ carbonFootprint, b1 }) { 

const phasesData = carbonFootprint?.value?.phases || {};

const values = {
  A1: phasesData.A1 || phasesData.A1_rawMaterials || 0,
  A2: phasesData.A2 || phasesData.A2_transportInbound || 0,
  A3: phasesData.A3 || phasesData.A3_production || 0,
  A4: phasesData.A4 || phasesData.A4_transportToUse || 0,
  B1: 0
};
  const total = values.A1 + values.A2 + values.A3 + values.A4 + values.B1;

  return (
    <Box sx={{ p: 2 }}>
      <Grid container spacing={1}>
        {/* Text-Teil */}
        <Grid item xs={12} md={7}>
          <Typography sx={{ fontSize: 13, color: "#111", mb: 1 }}>
            CO₂ emissions from product (so far)
          </Typography>

          <Typography sx={{ fontSize: 64, fontWeight: 700, color: "#111", mb: 2 }}>
            {total.toFixed(3)}
            <span style={{ fontSize: 36, fontWeight: 300 }}> kg</span>
          </Typography>

          <Typography sx={{ fontSize: 13, color: "#111", mb: 2 }}>
            Emissions calculated based on product life cycle
          </Typography>

          <div>
           {phases.map((phase) => {
  const value = values[phase.key];
              if ((phase.key !== "B1") && (!value || value <= 0)) {
                return null; // überspringen
              }

              const label = typeof phase.label === "function"
                ? phase.label(value)
                : phase.label;

              return (
                <div 
                  key={phase.key}
                  style={{ display: "flex", alignItems: "center", marginBottom: 8, marginLeft: 8 }}
                >
                  <div style={{ marginRight: 8 }}>
                    {value && phase.key !== "B1"
                      ? <CheckCircleIcon style={{ color: teal[700], fontSize: 24 }} />
                      : <RadioButtonUncheckedIcon style={{ color: grey[300], fontSize: 24 }} />}
                  </div>
                  <div style={{
                    fontSize: 20,
                    fontWeight: 400,
                    color: (phase.key === "B1") ? "#888" : "#111",
                  }}>
                    {label}
                  </div>
                </div>
              );
            })}
          </div>
        </Grid>

        {/* Diagramm */}
        <Grid item xs={12} md={5}>
          <StackedCO2Bar values={values} />
        </Grid>
      </Grid>
    </Box>
  );
}

function SubmodelContent({ submodel, latestB1 }) {
  const markerRefs = useRef([]);
  const mapRef = useRef();
  const [selected, setSelected] = useState(null);

  if (!submodel) return null;

if (submodel.idShort === "BillOfMaterials" && Array.isArray(submodel.submodelElements)) {
  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Bill of Materials
      </Typography>
      {submodel.submodelElements.map((group, idx) => {
        const items = Array.isArray(group.value) ? group.value : [];
        const hasAnyLink = items.some(p => !!p.link);
        return (
          <Box key={group.idShort} sx={{ mb: 4 }}>
            <Typography
              variant="h5"
              sx={{
                fontWeight: 600,
                mt: 2,
                mb: 1,
                fontSize: '1.13rem',
                color: "#111"
              }}
            >
              {group.idShort.replace(/_/g, " ")}
            </Typography>
            <table style={{
              background: '#fcfdff',
              marginBottom: 12,
              borderCollapse: 'collapse',
              width: '30%', // oder auto
              minWidth: 350
            }}>
              <thead style={{ background: "#f3f7fa" }}>
                <tr>
                  <th style={{ textAlign: 'left', fontWeight: 700, padding: "7px 14px 7px 10px", fontSize: 15 }}>Bezeichnung</th>
                  <th style={{ textAlign: 'left', fontWeight: 700, padding: "7px 6px", fontSize: 15, width: 40 }}>Stück</th>
                  {hasAnyLink && (
                    <th style={{ textAlign: 'left', fontWeight: 700, padding: "7px 6px", fontSize: 15, width: 30 }}>Link</th>
                  )}
                </tr>
              </thead>
              <tbody>
                {items.map((p, i) => (
                  <tr key={i}>
                    <td style={{ padding: "7px 14px 7px 10px", fontWeight: 500 }}>{p.idShort.replace(/_/g, " ")}</td>
                    <td style={{ padding: "7px 6px", verticalAlign: 'middle' }}>{p.value}</td>
                    {hasAnyLink && (
                      <td style={{ padding: "7px 6px", verticalAlign: 'middle' }}>
                        {p.link && (
                          <a
                            href={p.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            title="Externer Link"
                            style={{ color: "#111" }}
                          >
                            <OpenInNewIcon fontSize="small" />
                          </a>
                        )}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </Box>
        );
      })}
    </Box>
  );
}

// CarbonFootprint Submodell
if (submodel.idShort === "CarbonFootprint") {
  const cfProperty = submodel.submodelElements?.find(
    e => e.idShort === "CFPhases" || (e.modelType === "Property" && e.value?.phases)
  );

  const summarySource = cfProperty || submodel;

  // BauteilMarkers für Map + Liste
  const bauteilMarkers = extractBauteilMarkersFromCF(submodel);

  const groupedMarkers = {};
  for (const m of bauteilMarkers) {
    const key = `${m.lat},${m.lon}`;
    if (!groupedMarkers[key]) groupedMarkers[key] = [];
    groupedMarkers[key].push(m);
  }
  const groupedMarkerArr = Object.entries(groupedMarkers);

  const handleListClick = (idx, lat, lon) => {
    setSelected(idx);
    if (mapRef.current) {
      mapRef.current.flyTo([lat, lon], 13, { duration: 0.5 });
    }
    if (markerRefs.current[idx]) {
      markerRefs.current[idx].openPopup();
    }
  };

  return (
    <div>
      {/* Summary immer anzeigen */}
      <CarbonFootprintSummary carbonFootprint={summarySource} b1={latestB1} />

      <Typography sx={{ mb: 1, fontWeight: 700, fontSize: 20 }}>
        Product Journey:
      </Typography>

      <div style={{ display: 'flex', flexDirection: 'row', height: 350 }}>
        {/* Map */}
        <div style={{ width: 700, borderRadius: 8, overflow: "hidden", flexShrink: 0, marginRight: 18 }}>
          <MapContainer
            center={
              bauteilMarkers.length
                ? [bauteilMarkers[0].lat, bauteilMarkers[0].lon]
                : [48.21, 16.37]
            }
            zoom={7}
            scrollWheelZoom={false}
            style={{ height: 350, width: 700, borderRadius: 8 }}
            whenCreated={(mapInstance) => { mapRef.current = mapInstance; }}
          >
            <TileLayer
              attribution='&copy; OpenStreetMap'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <FitBounds markers={bauteilMarkers} />

            {groupedMarkerArr.map(([key, group], i) => (
              <Marker
                key={key + i}
                position={[group[0].lat, group[0].lon]}
                icon={svgIcon}
                ref={el => markerRefs.current[i] = el}
                eventHandlers={{ click: () => setSelected(i) }}
              >
                <Popup>
                  {group.map((el, idx) => (
                    <div key={idx} style={{ marginBottom: 8 }}>
                      <b>{el.name}</b><br />
                      {el.address}
                      {idx < group.length - 1 && <hr style={{ margin: "5px 0" }} />}
                    </div>
                  ))}
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>

        {/* Scrollbare Liste */}
        <div style={{
          flex: 1,
          maxHeight: 350,
          overflowY: 'auto',
          background: "#f9fafd",
          borderRadius: 8,
          border: "1px solid #eaeaea",
          padding: "0.5rem"
        }}>
          <Typography sx={{ fontWeight: 700, fontSize: 16, mb: 1 }}>
            List of Component Locations
          </Typography>

          <ul style={{ listStyle: 'none', margin: 0, padding: 0 }}>
            {groupedMarkerArr.map(([key, group], i) => (
              <li
                key={key + i}
                style={{
                  cursor: 'pointer',
                  background: selected === i ? '#d1e2fa' : 'transparent',
                  borderRadius: '6px',
                  padding: '7px 8px',
                  margin: '2px 0'
                }}
                onClick={() => handleListClick(i, group[0].lat, group[0].lon)}
              >
                {group.length === 1 ? (
                  <>
                    <b>{group[0].name}</b><br />
                    <span style={{ color: "#677", fontSize: 13 }}>{group[0].address}</span>
                  </>
                ) : (
                  <>
                    <b>{group.length} Components:</b><br />
                    {group.map((el, idx) => (
                      <span key={idx}>
                        • <b>{el.name}</b> – <span style={{ color: "#677", fontSize: 13 }}>{el.address}</span>
                        <br />
                      </span>
                    ))}
                  </>
                )}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Footer */}
      <div style={{ marginTop: 20 }}>
        <div style={{ color: "#76777A", fontSize: 16, marginBottom: 2 }}>
          Calculation Method
        </div>
        <a
          href="https://ghgprotocol.org/"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            textDecoration: "none",
            display: "inline-flex",
            alignItems: "center"
          }}
        >
          <span style={{
            color: "#000000ff",
            fontSize: 25,
            fontWeight: 700,
            letterSpacing: "0.5px"
          }}>
            GHG Protocol
          </span>
          <OpenInNewIcon
            style={{
              color: "#000000ff",
              marginLeft: 7,
              fontSize: 23,
              position: "relative",
              top: 2
            }}
          />
        </a>
      </div>
    </div>
  );
}

if (submodel.idShort === "EndOfLife" && Array.isArray(submodel.submodelElements)) {
  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        End Of Life
      </Typography>

      {submodel.submodelElements.map((group, idx) => {
        const items = Array.isArray(group.value) ? group.value : [];

        return (
          <Box key={group.idShort || idx} sx={{ mb: 4 }}>
            <Typography
              variant="h5"
              sx={{
                fontWeight: 600,
                mt: 2,
                mb: 1,
                fontSize: '1.13rem',
                color: "#111"
              }}
            >
              {group.idShort.replace(/_/g, " ")}
            </Typography>

            <table style={{
              background: '#fcfdff',
              marginBottom: 12,
              borderCollapse: 'collapse',
              width: '60%',
              minWidth: 400
            }}>
              <thead style={{ background: "#f3f7fa" }}>
                <tr>
                  <th style={{
                    textAlign: 'left',
                    fontWeight: 700,
                    padding: "7px 14px 7px 10px",
                    fontSize: 15
                  }}>
                    Bezeichnung / Entsorgung & Recycling
                  </th>
                </tr>
              </thead>
              <tbody>
                {items.map((p, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #eee" }}>
                    <td style={{ padding: "8px 14px 10px 10px" }}>
                      <div style={{ fontWeight: 500, marginBottom: 2 }}>
                        {p.idShort.replace(/_/g, " ")}
                      </div>
                      <div style={{ fontWeight: 400, color: "#444" }}>
                        {p.value}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Box>
        );
      })}
    </Box>
  );
}

  if (submodel.idShort === "BauteilAdressen") {
    const bauteilMarkers = extractBauteilMarkersFromCF(submodel);
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Bauteil Adressen
        </Typography>
        <Grid container spacing={2}>
          {bauteilMarkers.map((marker, i) => (
            <Grid item xs={12} sm={6} key={i}>
              <Box sx={{ mb: 1, p: 2, bgcolor: '#f9f9fb', borderRadius: 2, border: '1px solid #efefef' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>{marker.name}</Typography>
                <div>{marker.address}</div>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
}

  if(submodel.idShort === "Datasheets" && Array.isArray(submodel.submodelElements)) {
  // Sortiere/gruppiere
  const grouped = {};
  submodel.submodelElements.forEach((el) => {
    const catKey = resolveCategory(el.idShort || "");
    if (!grouped[catKey]) grouped[catKey] = [];
    grouped[catKey].push(el);
  });

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        {submodel.idShort || submodel.id}
      </Typography>
      {Object.entries(grouped).map(([catKey, elements]) => (
  <div key={catKey}>
    <Typography
      variant="h4"
      sx={{
        fontWeight: 400,
        mt: 2,
        mb: 1.5,
        fontSize: '1.10rem',
        color: "#111"
      }}
    >
      {CATEGORY_MAPPING[catKey] || catKey}
    </Typography>
    <Grid container spacing={2}>
      {elements.map((el, i) => {
              const getFromValue = (idShort) =>
                (el.value || []).find(v => v.idShort === idShort);
              const className = getFromValue("ClassName")?.value;
              const classificationSystem = getFromValue("ClassificationSystem")?.value;
              const documentVersion = (el.value || []).find(v => (v.idShort || "").startsWith("DocumentVersion"));
              let title=[], setDate="", orgName="", pdfLink="";
              if (documentVersion && Array.isArray(documentVersion.value)) {
                const titleEl = documentVersion.value.find(x => x.idShort === "Title");
                if (titleEl && Array.isArray(titleEl.value)) {
                  title = titleEl.value;
                }
                setDate = documentVersion.value.find(x => x.idShort === "SetDate")?.value || "";
                orgName = documentVersion.value.find(x => x.idShort === "OrganizationName")?.value || "";
                pdfLink = documentVersion.value.find(x => x.modelType === "File" && x.value)?.value || "";
              }
              return (
                <Grid item xs={12} sm={6} key={i}>
                  <Box sx={{
                    mb: 1, p: 2, bgcolor: '#f9f9fb', borderRadius: 2,
                    border: '1px solid #efefef', minHeight: 150
                  }}>
                    <Typography variant="subtitle1" sx={{fontWeight:600}}>{el.idShort}</Typography>
                    <div><b>OrganizationName:</b> {orgName}</div>
                    <div><b>ClassName:</b> {className}</div>
                    <div><b>ClassificationSystem:</b> {classificationSystem}</div>
                    <div><b>SetDate:</b> {setDate}</div>
                    {pdfLink && (
                      <a href={pdfLink} target="_blank" rel="noopener noreferrer">
                        <button style={{
                          padding: '7px 16px',
                          color: 'white',
                          backgroundColor: '#2656c2',
                          border: 'none',
                          borderRadius: 5,
                          cursor: 'pointer',
                          margin: '16px 0 0 0'
                        }}>
                          PDF öffnen
                        </button>
                      </a>
                    )}
                  </Box>
                </Grid>
              );
            })}
          </Grid>
        </div>
      ))}
    </Box>
  );
}
// Nameplate Submodell
if (submodel.idShort === 'Nameplate') {
  const nameplateExcludeIds = ["Marking_CE", "Marking_CRUUS", "Marking_RCM", "YearOfConstruction"];
  const elements = (submodel.submodelElements || []).filter(
    el => !nameplateExcludeIds.includes(el.idShort)
  );

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        {submodel.idShort}
      </Typography>
      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {elements.map((el, i) => {

        if (el.idShort === "ProductionDateTime") {
          return (
            <Box
              key={i}
              sx={{
                p: 2,
                bgcolor: '#f9f9fb',
                borderRadius: 2,
                border: '1px solid #eaeaea',
                maxWidth: "600px",
                width: "100%",
                marginBottom: "1px"
              }}
            >
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                ProductionDateTime
              </Typography>
              <div>
                {new Date(el.value).toLocaleString("de-DE", {
                  day: "2-digit",
                  month: "2-digit",
                  year: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                  second: "2-digit"
                })}
              </div>
            </Box>
          );
        }

        if (el.idShort === "PhysicalAddress" && Array.isArray(el.value)) {
          const addrMap = {};
          el.value.forEach(v => { addrMap[v.idShort] = v.value; });

          return (
            <Box
                key={i}
                sx={{
                  p: 2,
                  bgcolor: '#f9f9fb',
                  borderRadius: 2,
                  border: '1px solid #eaeaea',
                  maxWidth: "600px",
                  width: "100%",
                  marginBottom: "1px"
                }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                Physical Address
              </Typography>
              <div>Department: {addrMap.Department}</div>
              <div>Street: {addrMap.Street}</div>
              <div>Zipcode: {addrMap.Zipcode}</div>
              <div>CityTown: {addrMap.CityTown}</div>
              <div>NationalCode: {addrMap.NationalCode}</div>
              <div>StateCounty: {addrMap.StateCounty}</div>
              <div>Office: {addrMap.Office}</div>
              <div>
                Email:{" "}
                <a href={`mailto:${addrMap.Email}`}>
                  {addrMap.Email}
                </a>
              </div>
              <div>
                Website:{" "}
                <a href={addrMap.Website} target="_blank" rel="noopener noreferrer">
                  {addrMap.Website}
                </a>
              </div>
            </Box>
          );
        }

          return (
            <Box
                key={i}
                sx={{
                  p: 2,
                  bgcolor: '#f9f9fb',
                  borderRadius: 2,
                  border: '1px solid #eaeaea',
                  maxWidth: "600px",
                  width: "100%",
                  marginBottom: "1px"
                }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                {el.idShort}
              </Typography>
              <div>{typeof el.value === "string" ? el.value : JSON.stringify(el.value)}</div>
            </Box>
          );
        })}
      </div>
    </Box>
  );
}

return (
  <Box sx={{ p: 2 }}>
    <Typography variant="h6" gutterBottom>
      {submodel.idShort || submodel.id}
    </Typography>
    <pre style={{ background: "#f3f3f3", padding: 10, borderRadius: 6 }}>
      {JSON.stringify(submodel.submodelElements, null, 2)}
    </pre>
  </Box>
);
}

export default function App() {
  const [pid, setPid] = useState("1");

  /* Produktpass laden */
  const dpp        = useDpp(pid);
  const submodels  = dpp?.submodels || [];

  /* Sidebar-Auswahl */
  const [selected, setSelected] = useState(0);
  React.useEffect(() => { setSelected(0); }, [dpp]);

  /* Live-CO₂ für B1 holen */
  const latestB1 = useLatestUsageCO2();

  /* Simulation State */
  const [simRunning, setSimRunning] = useState(false);
  const [timeline, setTimeline] = useState([]);

  // Polling
  useEffect(() => {
    const interval = setInterval(() => {
      axios.get("http://localhost:8000/product_passes?limit=10")
           .then(res => setTimeline(res.data));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const startSimulation = () => {
    axios.post("http://localhost:8000/start_simulation")
         .then(() => setSimRunning(true));
  };

  const stopSimulation = () => {
    axios.post("http://localhost:8000/stop_simulation")
         .then(() => setSimRunning(false));
  };

  return (
    <Box sx={{ bgcolor: "#f6faff", minHeight: "100vh", p: 2 }}>
      {/* Kopfzeile */}
      <div style={{ marginBottom: 20 }}>
        <label>
          <b>Produktpass-ID:&nbsp;</b>
          <input
            value={pid}
            onChange={e => setPid(e.target.value)}
            style={{ marginRight: 10 }}
          />
        </label>
      </div>

      {/* Simulation Controls */}
      <div style={{ marginBottom: 20 }}>
        <button onClick={startSimulation} disabled={simRunning}>
          ▶ Start Simulation
        </button>
        <button onClick={stopSimulation} disabled={!simRunning} style={{ marginLeft: 10 }}>
          ⏹ Stop Simulation
        </button>
      </div>

      {/* Timeline */}
      <div style={{ marginBottom: 20 }}>
        <h3>Produktions-Timeline</h3>
        <ul>
          {timeline.map(entry => {
            const prodTimeRaw = entry.data.submodels
              ?.find(sm => sm.idShort === "Nameplate")
              ?.submodelElements.find(e => e.idShort === "ProductionDateTime")?.value;

            let prodTimeFormatted = prodTimeRaw
              ? new Date(prodTimeRaw).toLocaleString("de-DE", {
                  day: "2-digit",
                  month: "2-digit",
                  year: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                  second: "2-digit"
                })
              : "";

            return (
              <li key={entry.id}>
                DPP {entry.id} produced at {prodTimeFormatted}
              </li>
            );
          })}
        </ul>
      </div>

      {/* Hauptbereich */}
      {dpp ? (
        <>
          <AssetInfo shell={dpp.assetAdministrationShells?.[0]} />
          <Card>
            <Box sx={{ display: "flex", flexDirection: "row" }}>
              <Box sx={{ minWidth: 240, borderRight: 1, borderColor: "#ddd", bgcolor: "#f7fafd" }}>
                <SubmodelSidebar
                  submodels={submodels}
                  selected={selected}
                  setSelected={setSelected}
                />
              </Box>
              <Box sx={{ flex: 1, p: 2 }}>
                <SubmodelContent submodel={submodels[selected]} latestB1={latestB1} />
              </Box>
            </Box>
          </Card>
        </>
      ) : (
        <div>Kein Produktpass gefunden.</div>
      )}
    </Box>
  );
}