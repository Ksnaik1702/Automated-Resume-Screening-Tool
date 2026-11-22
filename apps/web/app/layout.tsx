import React from 'react'

export const metadata = {
  title: 'Automated Resume Screening ATS Dashboard',
  description: 'Production Recruiter Portal for candidate ranking and skill gap inspection',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <script src="https://cdn.tailwindcss.com"></script>
      </head>
      <body className="bg-slate-50 text-slate-900 min-h-screen">
        {children}
      </body>
    </html>
  )
}
