# Phase 7: Production Readiness and Iteration

This phase finalizes the application by setting up robust deployment configurations, documenting operational procedures, and defining the roadmap for Version 2.

## Directory Structure
- `deploy/`: Contains all the configuration files required to deploy the backend to Railway.
- `docs/`: Contains production documentation including the Runbook, Prompt Strategy, and V2 Roadmap.

## Deployment Instructions (Railway)

**CRITICAL NOTE:** Railway's automatic builder (Nixpacks) requires deployment configuration files to be at the **root** of your repository. 

Before pushing to GitHub to trigger a deployment, you must copy the contents of the `deploy/` folder to the root directory of your project:

1. Copy `deploy/requirements.txt` to the root folder.
2. Copy `deploy/Procfile` to the root folder.
3. Copy `deploy/start_backend.sh` to the root folder.

Once these files are at the root, simply commit and push:
```bash
git add .
git commit -m "Deploy Phase 7 Configuration"
git push origin main
```

For full deployment and troubleshooting instructions for both Railway and Vercel, please refer to the [Runbook](./docs/runbook.md).
