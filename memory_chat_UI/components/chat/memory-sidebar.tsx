"use client"

import { Brain, Trash2, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface Memory {
  id: string
  fact: string
}

interface MemorySidebarProps {
  memories: Memory[]
  onClearMemory: () => void
  isOpen: boolean
  onClose: () => void
}

export function MemorySidebar({ memories, onClearMemory, isOpen, onClose }: MemorySidebarProps) {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <aside
        className={cn(
          "fixed lg:relative inset-y-0 right-0 z-50 w-72 bg-card border-l border-border flex flex-col transition-transform duration-300 lg:translate-x-0",
          isOpen ? "translate-x-0" : "translate-x-full"
        )}
      >
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-primary" />
            <h2 className="font-semibold text-sm">Active Memories</h2>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden h-8 w-8"
            onClick={onClose}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {memories.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              No memories stored yet. Start chatting to build context.
            </p>
          ) : (
            <ul className="space-y-2">
              {memories.map((memory) => (
                <li
                  key={memory.id}
                  className="text-sm p-3 rounded-lg bg-secondary/50 border border-border/50 text-secondary-foreground"
                >
                  {memory.fact}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="p-4 border-t border-border">
          <Button
            variant="outline"
            size="sm"
            className="w-full gap-2 text-destructive hover:text-destructive hover:bg-destructive/10"
            onClick={onClearMemory}
            disabled={memories.length === 0}
          >
            <Trash2 className="h-4 w-4" />
            Clear Memory
          </Button>
        </div>
      </aside>
    </>
  )
}
