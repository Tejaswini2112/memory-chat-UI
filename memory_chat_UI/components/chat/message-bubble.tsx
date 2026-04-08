"use client"

import { cn } from "@/lib/utils"

interface MessageBubbleProps {
  content: string
  timestamp: Date
  isUser: boolean
}

export function MessageBubble({ content, timestamp, isUser }: MessageBubbleProps) {
  const formattedTime = timestamp.toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  })

  return (
    <div className={cn("flex flex-col gap-1", isUser ? "items-end" : "items-start")}>
      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed",
          isUser
            ? "bg-primary text-primary-foreground rounded-br-md"
            : "bg-secondary text-secondary-foreground rounded-bl-md"
        )}
      >
        {content}
      </div>
      <span className="text-[10px] text-muted-foreground px-1" suppressHydrationWarning>
        {formattedTime}
      </span>
    </div>
  )
}
