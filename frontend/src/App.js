import { useState } from "react";
import axios from "axios";

const API = "http://127.0.0.1:8000";

function App() {
  const [token, setToken] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [file, setFile] = useState(null);
  const [targetLang, setTargetLang] = useState("ur");
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState("");
  const [progress, setProgress] = useState(0);
  const [done, setDone] = useState(false);
  const [screen, setScreen] = useState("login");

  const login = async () => {
    const res = await axios.post(`${API}/api/token/`, { username, password });
    setToken(res.data.access);
    setScreen("upload");
  };

  const upload = async () => {
    const form = new FormData();
    form.append("file", file);
    form.append("file_format", "pdf");
    const res = await axios.post(`${API}/api/file/`, form, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const fileId = res.data.id;
    const jobRes = await axios.post(
      `${API}/api/jobs/`,
      { input_file: fileId, source_lang: "en", target_lang: targetLang },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    setJobId(jobRes.data.id);
    setScreen("progress");
    poll(jobRes.data.id);
  };

  const poll = (id) => {
    const interval = setInterval(async () => {
      const res = await axios.get(`${API}/api/jobs/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setStatus(res.data.status);
      setProgress(res.data.progress);
      if (res.data.status === "done" || res.data.status === "failed") {
        clearInterval(interval);
        if (res.data.status === "done") setDone(true);
        setScreen("download");
      }
    }, 5000);
  };

  const download = async () => {
    const res = await axios.get(`${API}/api/jobs/${jobId}/download/`, {
      headers: { Authorization: `Bearer ${token}` },
      responseType: "blob",
    });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "translated.pdf");
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  if (screen === "login") return (
    <div style={styles.container}>
      <h1 style={styles.title}>PDF Translator</h1>
      <input style={styles.input} placeholder="Username" onChange={e => setUsername(e.target.value)} />
      <input style={styles.input} placeholder="Password" type="password" onChange={e => setPassword(e.target.value)} />
      <button style={styles.button} onClick={login}>Login</button>
    </div>
  );

  if (screen === "upload") return (
    <div style={styles.container}>
      <h1 style={styles.title}>Upload PDF</h1>
      <input type="file" accept=".pdf" onChange={e => setFile(e.target.files[0])} style={styles.input} />
      <select style={styles.input} onChange={e => setTargetLang(e.target.value)}>
        <option value="ur">Urdu</option>
        <option value="ar">Arabic</option>
        <option value="fr">French</option>
        <option value="es">Spanish</option>
      </select>
      <button style={styles.button} onClick={upload}>Translate</button>
    </div>
  );

  if (screen === "progress") return (
    <div style={styles.container}>
      <h1 style={styles.title}>Translating...</h1>
      <p style={styles.status}>Status: {status}</p>
      <div style={styles.barBg}>
        <div style={{ ...styles.bar, width: `${progress}%` }} />
      </div>
      <p style={styles.status}>{progress.toFixed(1)}% complete</p>
    </div>
  );

  if (screen === "download") return (
    <div style={styles.container}>
      <h1 style={styles.title}>{done ? "Translation Complete!" : "Translation Failed"}</h1>
      {done && <button style={styles.button} onClick={download}>Download PDF</button>}
      <button style={{ ...styles.button, background: "#666" }} onClick={() => { setScreen("upload"); setDone(false); }}>
        Translate Another
      </button>
    </div>
  );
}

const styles = {
  container: { maxWidth: 480, margin: "80px auto", padding: 32, fontFamily: "sans-serif", textAlign: "center" },
  title: { fontSize: 28, marginBottom: 24, color: "#1a1a1a" },
  input: { display: "block", width: "100%", padding: "12px", marginBottom: 16, fontSize: 16, borderRadius: 8, border: "1px solid #ddd", boxSizing: "border-box" },
  button: { width: "100%", padding: "14px", fontSize: 16, background: "#534AB7", color: "#fff", border: "none", borderRadius: 8, cursor: "pointer", marginBottom: 12 },
  status: { color: "#666", marginBottom: 12 },
  barBg: { background: "#eee", borderRadius: 8, height: 12, marginBottom: 12 },
  bar: { background: "#534AB7", height: 12, borderRadius: 8, transition: "width 0.5s" },
};

export default App;