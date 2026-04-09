"use client"

import { useState, useEffect, useRef } from "react"
import { Brain, Menu } from "lucide-react"
import { Button } from "@/components/ui/button"
import { MessageBubble } from "./message-bubble"
import { TypingIndicator } from "./typing-indicator"
import { MemorySidebar } from "./memory-sidebar"
import { ChatInput } from "./chat-input"
import { ThemeToggle } from "./theme-toggle"

interface Message {
  id: string
  content: string
  timestamp: Date
  isUser: boolean
}

interface Memory {
  id: string
  fact: string
}

const initialMessages: Message[] = [
  {
    id: "1",
    content: "Hello! I'm your memory assistant. I can remember important details about our conversations. What would you like to chat about?",
    timestamp: new Date(Date.now() - 60000),
    isUser: false,
  },
]

const initialMemories: Memory[] = []

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [memories, setMemories] = useState<Memory[]>(initialMemories)
  const [isTyping, setIsTyping] = useState(false)
  const [isDark, setIsDark] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
  }, [isDark])

  const handleSendMessage = async (content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      content,
      timestamp: new Date(),
      isUser: true,
    }

    setMessages((prev) => [...prev, newMessage])
    setIsTyping(true)

    try {
      // Call the FastAPI backend
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: content }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || "Failed to fetch response")
      }

      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: data.reply,
        timestamp: new Date(),
        isUser: false,
      }
      setMessages((prev) => [...prev, botResponse])

      // Update memories from backend smart memory
      if (data.memory && data.memory.length > 0) {
        setMemories(
          data.memory.map((fact: string, idx: number) => ({
            id: idx.toString(),
            fact,
          }))
        )
      }
    } catch (error) {
      console.error("Chat error:", error)
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, I ran into an error connecting to the API.",
        timestamp: new Date(),
        isUser: false,
      }
      setMessages((prev) => [...prev, errorResponse])
    } finally {
      setIsTyping(false)
    }
  }

  const handleClearMemory = async () => {
    try {
      await fetch("http://localhost:8000/api/clear/default", { method: "DELETE" })
      setMemories([])
    } catch (error) {
      console.error("Failed to clear memory:", error)
    }
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="flex items-center justify-between px-4 py-3 border-b border-border bg-card">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-full bg-primary/10 flex items-center justify-center">
              <Brain className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h1 className="font-semibold text-sm">Memory Bot</h1>
              <p className="text-xs text-muted-foreground">Always here to help</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle isDark={isDark} onToggle={() => setIsDark(!isDark)} />
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden h-9 w-9"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="h-5 w-5" />
              <span className="sr-only">Open memories</span>
            </Button>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto p-4 space-y-4">
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                content={message.content}
                timestamp={message.timestamp}
                isUser={message.isUser}
              />
            ))}
            {isTyping && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input */}
        <ChatInput onSendMessage={handleSendMessage} disabled={isTyping} />
      </div>

      {/* Memory Sidebar */}
      <MemorySidebar
        memories={memories}
        onClearMemory={handleClearMemory}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />
    </div>
  )
}
