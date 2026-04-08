"use client"

export function TypingIndicator() {
  return (
    <div className="flex items-start">
      <div className="bg-secondary rounded-2xl rounded-bl-md px-4 py-3">
        <div className="flex gap-1">
          <span className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce [animation-delay:-0.3s]" />
          <span className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce [animation-delay:-0.15s]" />
          <span className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" />
        </div>
      </div>
    </div>
  )
}
