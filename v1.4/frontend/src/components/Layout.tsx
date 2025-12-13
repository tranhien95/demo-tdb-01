import React from 'react'

interface LayoutProps {
  children: React.ReactNode
  title: string
  description?: string
  actions?: React.ReactNode
}

export const Layout: React.FC<LayoutProps> = ({ children, title, description, actions }) => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="gradient-header rounded-2xl p-6 shadow-xl">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold">{title}</h2>
            {description && (
              <p className="text-sm opacity-90 mt-1">{description}</p>
            )}
          </div>
          {actions && (
            <div className="flex gap-2">
              {actions}
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      {children}
    </div>
  )
}

