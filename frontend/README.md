# Music Player

A simple, modern music player interface built with React Router and Tailwind CSS.

## Features

- 🎵 Simple music player interface
- 🎨 Dark theme design
- 📱 Responsive layout
- ⚡️ Hot Module Replacement (HMR)
- 🔄 Real-time audio controls
- 🔒 TypeScript by default
- 🎉 TailwindCSS for styling

## Getting Started

### Installation

Install the dependencies:

```bash
npm install
```

### Development

Start the development server with HMR:

```bash
npm run dev
```

Your music player will be available at `http://localhost:5173`.

## Features

- **Play/Pause Controls**: Simple play and pause functionality
- **Progress Bar**: Seek through tracks with a clickable progress bar
- **Volume Control**: Adjust volume with a slider
- **Track List**: Switch between different tracks
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Customization

To add your own music:

1. Replace the `sampleTracks` array in `app/routes/home.tsx`
2. Add your own audio files and update the URLs
3. Customize the track information (title, artist)

## Building for Production

Create a production build:

```bash
npm run build
```

## Deployment

### Docker Deployment

To build and run using Docker:

```bash
docker build -t music-player .

# Run the container
docker run -p 3000:3000 music-player
```

The containerized application can be deployed to any platform that supports Docker.

---

Built with ❤️ using React Router and Tailwind CSS.
