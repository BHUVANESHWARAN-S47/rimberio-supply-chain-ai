import JSZip from 'jszip';
import { saveAs } from 'file-saver';

export const exportProjectAsZip = async () => {
  const zip = new JSZip();

  // Root files
  zip.file(
    'package.json',
    JSON.stringify(
      {
        name: 'rimberio-ai-supply-chain',
        private: true,
        version: '1.0.0',
        type: 'module',
        scripts: {
          dev: 'vite',
          build: 'vite build',
          preview: 'vite preview',
        },
        dependencies: {
          'file-saver': '^2.0.5',
          jszip: '^3.10.1',
          'lucide-react': '^0.475.0',
          react: '^19.0.0',
          'react-dom': '^19.0.0',
        },
        devDependencies: {
          '@tailwindcss/vite': '^4.0.0',
          '@types/react': '^19.0.0',
          '@types/react-dom': '^19.0.0',
          '@vitejs/plugin-react': '^4.3.4',
          tailwindcss: '^4.0.0',
          vite: '^6.1.0',
        },
      },
      null,
      2
    )
  );

  zip.file(
    'vite.config.js',
    `import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})`
  );

  zip.file(
    'index.html',
    `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>RIMBERIO — AI Supply Chain Intelligence Platform</title>
  </head>
  <body class="bg-[#0b1329] text-slate-100 antialiased">
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>`
  );

  zip.file(
    'README.md',
    `# RIMBERIO — Autonomous AI Supply Chain & Digital Twin Platform

Welcome to **RIMBERIO AI Supply Chain Platform**, an enterprise-grade digital twin platform that leverages multi-agent negotiations, predictive disruption simulation, and real-time risk mitigation.

## 🚀 Quick Start Guide

1. **Install Dependencies**:
   \`\`\`bash
   npm install
   \`\`\`

2. **Start Development Server**:
   \`\`\`bash
   npm run dev
   \`\`\`

3. **Build Production Bundle**:
   \`\`\`bash
   npm run build
   \`\`\`

## 📦 Features Included

- 🔑 **Enterprise Authentication**: Login, Sign Up, and Password Reset screens
- 📊 **Supply Chain Twin Dashboard**: Live network map, disruption telemetry & risk alerts
- 🤖 **Multi-Agent Negotiation Console**: Real-time buyer vs. supplier AI negotiation engine
- ⚡ **Counterfactual Simulation**: What-if scenario analysis for supply disruptions
- 🏢 **Supplier Management Workspace**: Multi-criteria supplier performance scorecards
- 🎯 **Adaptive Decision Center**: SLA impact analysis and automated mitigation triggers
- 📈 **Reports & Architecture**: Audit logs, connectivity matrix, and system report exporter
- 📥 **Source Code Downloader**: Interactive ZIP exporter built directly into the UI

Created for RIMBERIO Global Logistics Dynamics.
`
  );

  // Generate ZIP blob and save
  const content = await zip.generateAsync({ type: 'blob' });
  saveAs(content, 'rimberio-ai-supply-chain-react-app.zip');
};
