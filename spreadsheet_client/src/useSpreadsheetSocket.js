import { useEffect, useRef } from "react";
import { io } from "socket.io-client";

// Detect if running inside Docker vs local dev
const isDocker =
  window.location.hostname !== "localhost" &&
  window.location.hostname !== "127.0.0.1";

const SOCKET_URL = isDocker
  ? import.meta.env.VITE_DOCKER_API_BASE_URL || "http://spreadsheet_backend:5000"
  : import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

export function useSpreadsheetSocket(onCellUpdate) {
  const socketRef = useRef(null);

  useEffect(() => {
    if (!socketRef.current) {
      console.log(`🔌 Connecting to socket at ${SOCKET_URL}`);
      const socket = io(SOCKET_URL, {
        transports: ["websocket"],
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000,
      });

      socket.on("connect", () => console.log("✅ Connected to backend"));
      socket.on("disconnect", (reason) =>
        console.log("🔌 Disconnected from backend:", reason)
      );
      socket.on("connect_error", (err) =>
        console.error("❌ Socket connection error:", err)
      );

      // Listen for backend updates
      socket.on("cell_update", (data) => {
        console.log("📡 Received update:", data);
        if (onCellUpdate) onCellUpdate(data.update);
      });

      socketRef.current = socket;
    }

    // 👇 Cleanup only once, when component unmounts
    return () => {
      if (socketRef.current) {
        console.log("🧹 Cleaning up socket connection");
        socketRef.current.disconnect();
        socketRef.current = null;
      }
    };
  }, []); // ⬅️ no dependencies (connect once only)

  return socketRef.current;
}
