import { useState, useRef, useEffect } from "react";
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Container,
  Avatar,
  CircularProgress,
  Alert,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import PersonIcon from "@mui/icons-material/Person";
import DescriptionIcon from "@mui/icons-material/Description";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import axios from "axios";

// API base URL
const API_BASE_URL = "http://localhost:8000";

// Message type
interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatUI() {
  const [uploaded, setUploaded] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [, setUploadedFileName] = useState("");

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle file selection
  const handleFileSelect = async (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith(".pdf")) {
      setUploadError("Please select a PDF file");
      return;
    }

    setUploadLoading(true);
    setUploadError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setUploaded(true);
      setUploadedFileName(file.name);
      // Add welcome message
      setMessages([
        {
          role: "assistant",
          content: `Hello! I've processed your resume "${file.name}". Ask me anything about it!`,
        },
      ]);
    } catch (err) {
      console.error("Upload error:", err);
      setUploadError(
        axios.isAxiosError(err)
          ? err.response?.data?.detail || "Failed to upload PDF"
          : "An unexpected error occurred",
      );
    } finally {
      setUploadLoading(false);
    }
  };

  // Trigger file input click
  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  // Handle sending message
  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setError(null);

    // Add user message to chat
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      // Prepare conversation history for API
      const history = messages
        .filter((m) => m.role !== "assistant" || messages.indexOf(m) > 0) // Skip initial greeting
        .map((m) => [
          m.content,
          messages[messages.indexOf(m) + 1]?.content || "",
        ])
        .filter((_, i) => i % 2 === 0); // Get pairs of Q&A

      // Call backend API
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        query: userMessage,
        history: history,
      });

      // Add assistant response
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.data.response },
      ]);
    } catch (err) {
      console.error("Error sending message:", err);
      setError(
        axios.isAxiosError(err)
          ? err.response?.data?.detail || "Failed to get response from server"
          : "An unexpected error occurred",
      );
    } finally {
      setLoading(false);
    }
  };

  // Handle Enter key
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Upload Screen
  if (!uploaded) {
    return (
      <Container
        maxWidth="sm"
        sx={{ height: "100vh", display: "flex", alignItems: "center" }}
      >
        <Paper elevation={3} sx={{ width: "100%", p: 4, borderRadius: 3 }}>
          <Box sx={{ textAlign: "center", mb: 3 }}>
            <DescriptionIcon
              sx={{ fontSize: 64, color: "primary.main", mb: 2 }}
            />
            <Typography variant="h4" sx={{ fontWeight: "bold" }} gutterBottom>
              Resume Chatbot
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Upload your resume PDF to start chatting
            </Typography>
          </Box>

          {uploadError && (
            <Alert
              severity="error"
              sx={{ mb: 2 }}
              onClose={() => setUploadError(null)}
            >
              {uploadError}
            </Alert>
          )}

          <input
            type="file"
            accept=".pdf"
            ref={fileInputRef}
            onChange={handleFileSelect}
            style={{ display: "none" }}
          />

          <Paper
            onClick={handleUploadClick}
            sx={{
              p: 4,
              border: "2px dashed",
              borderColor: uploadLoading ? "primary.main" : "grey.300",
              borderRadius: 2,
              textAlign: "center",
              cursor: uploadLoading ? "default" : "pointer",
              "&:hover": !uploadLoading && {
                borderColor: "primary.main",
                bgcolor: "action.hover",
              },
            }}
          >
            {uploadLoading ? (
              <Box>
                <CircularProgress size={48} sx={{ mb: 2 }} />
                <Typography variant="body1">
                  Processing your resume...
                </Typography>
              </Box>
            ) : (
              <Box>
                <CloudUploadIcon
                  sx={{ fontSize: 48, color: "grey.500", mb: 2 }}
                />
                <Typography variant="h6" sx={{ mb: 1 }}>
                  Click to upload PDF
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Only PDF files are supported
                </Typography>
              </Box>
            )}
          </Paper>
        </Paper>
      </Container>
    );
  }

  // Chat Screen
  return (
    <Container maxWidth="md" sx={{ height: "100vh", py: 2 }}>
      <Paper
        elevation={3}
        sx={{
          height: "100%",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          borderRadius: 3,
        }}
      >
        {/* Header */}
        <Box
          sx={{
            p: 2,
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            color: "white",
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <DescriptionIcon />
            <Typography variant="h6" sx={{ fontWeight: "bold" }}>
              Resume Chatbot
            </Typography>
          </Box>
          <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
            Ask questions about the uploaded resume PDF
          </Typography>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ m: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Messages Area */}
        <Box
          sx={{
            flex: 1,
            overflowY: "auto",
            p: 2,
            backgroundColor: "#f5f5f5",
          }}
        >
          {messages.map((message, index) => (
            <Box
              key={index}
              sx={{
                display: "flex",
                justifyContent:
                  message.role === "user" ? "flex-end" : "flex-start",
                mb: 2,
              }}
            >
              <Box
                sx={{
                  display: "flex",
                  flexDirection:
                    message.role === "user" ? "row-reverse" : "row",
                  gap: 1,
                  alignItems: "flex-start",
                  maxWidth: "80%",
                }}
              >
                <Avatar
                  sx={{
                    bgcolor: message.role === "user" ? "#667eea" : "#764ba2",
                    width: 32,
                  }}
                >
                  {message.role === "user" ? <PersonIcon /> : <SmartToyIcon />}
                </Avatar>
                <Paper
                  elevation={1}
                  sx={{
                    p: 1.5,
                    backgroundColor:
                      message.role === "user" ? "#667eea" : "white",
                    color: message.role === "user" ? "white" : "text.primary",
                    borderRadius: 2,
                  }}
                >
                  <Typography
                    variant="body1"
                    sx={{
                      whiteSpace: "pre-wrap",
                      wordBreak: "break-word",
                    }}
                  >
                    {message.content}
                  </Typography>
                </Paper>
              </Box>
            </Box>
          ))}
          {loading && (
            <Box sx={{ display: "flex", justifyContent: "flex-start", mb: 2 }}>
              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                <Avatar sx={{ bgcolor: "#764ba2", width: 32, height: 32 }}>
                  <SmartToyIcon />
                </Avatar>
                <Paper sx={{ p: 1.5, borderRadius: 2 }}>
                  <CircularProgress size={20} color="secondary" />
                </Paper>
              </Box>
            </Box>
          )}
          <div ref={messagesEndRef} />
        </Box>

        {/* Input Area */}
        <Box
          sx={{
            p: 2,
            backgroundColor: "white",
            borderTop: 1,
            borderColor: "divider",
          }}
        >
          <Box sx={{ display: "flex", gap: 1 }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Ask about the resume..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
              multiline
              maxRows={3}
              size="small"
            />
            <IconButton
              color="primary"
              onClick={handleSend}
              disabled={!input.trim() || loading}
              sx={{
                bgcolor: "primary.main",
                color: "white",
                "&:hover": { bgcolor: "primary.dark" },
                "&.Mui-disabled": { bgcolor: "grey.300", color: "grey.500" },
              }}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
}
