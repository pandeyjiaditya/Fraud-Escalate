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
import ResultsPageNew from "./pages/ResultsPageNew";
import ResultsHistory from "./pages/ResultsHistory";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/mail-terminal" element={<MailTerminal />} />
        <Route path="/upload-artifacts" element={<UploadArtifacts />} />
        <Route path="/results" element={<ResultsPageNew />} />
        <Route path="/results-history" element={<ResultsHistory />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}
