# Static Hosting Ready

This folder contains a static copy of the car game that can be deployed to a static host such as GitHub Pages, Netlify, or Vercel.

## How to publish

1. Push this repository to GitHub.
2. In the repository settings, enable GitHub Pages from the `docs` folder on the main branch.
3. Wait a few minutes and use the provided GitHub Pages URL to open the game.

## Why this solves the problem

- The game is now a static webpage and does not require this computer to stay turned on.
- External hosting keeps it available even after VS Code is closed.

## Notes

- Local high scores and servers are stored in the browser using localStorage.
- The URL will remain live as long as the hosting service stays active.
