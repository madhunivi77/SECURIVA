# SECURIVA
The project focuses on developing an AI-assisted platform that automates and manages key business operations while maintaining strong cybersecurity safeguards.




# Contributing Guidelines    
Following are the guidelines to ensure smooth collaboration and integration. 

---

## Branching Model
We follow a **GitHub Flow** style branching model:  

- **`main`** → Production-ready, stable code.  
- **`dev`** → Integration/testing branch.  
- **`feature/*`** → One branch per feature (e.g., `feature/login-auth`, `feature/api-integration`).  

**Rules:**  
- Do **not** commit directly to `main` or `dev`.  
- Always branch off from `dev`.  
- Create a Pull Request (PR) when a feature is ready.  

## Commit Message Conventions (Taiga Integration)
To keep GitHub and Taiga linked, reference Taiga task IDs in your commit messages:  

- `TG-123` ->Links commit to task/story **123**.  
- `TG-123` -> Closes task/story **123**.  
- `TG-123 ready for test` -> Moves task **123** to *Ready for Test*.  

**Examples:**  
```bash
git commit -m "Add login API TG-45"
git commit -m "Fix authentication bug TG-46"
git commit -m "Update test cases for signup TG-47"

