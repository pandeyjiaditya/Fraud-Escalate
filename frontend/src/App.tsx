import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import HomePage from "./pages/HomePage";
import MailTerminal from "./pages/MailTerminal";
import UploadArtifacts from "./pages/UploadArtifacts";
import ResultsPage from "./pages/ResultsPage";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/mail-terminal" element={<MailTerminal />} />
        <Route path="/upload-artifacts" element={<UploadArtifacts />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}
