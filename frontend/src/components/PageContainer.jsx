/**
 * PageContainer Component
 *
 * Consistent page layout wrapper for professional medical applications
 * Provides proper spacing, max-width, and optional breadcrumb area
 */

export default function PageContainer({ children, title, subtitle, breadcrumb }) {
  return (
    <div className="min-h-screen bg-gray-100">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Optional breadcrumb area */}
        {breadcrumb && <div className="mb-4 text-sm text-gray-600">{breadcrumb}</div>}

        {/* Page header */}
        {(title || subtitle) && (
          <div className="mb-6">
            {title && <h2 className="text-xl font-semibold text-gray-900 mb-1">{title}</h2>}
            {subtitle && <p className="text-sm text-gray-600">{subtitle}</p>}
          </div>
        )}

        {/* Main content */}
        <div className="space-y-6">{children}</div>
      </main>
    </div>
  );
}
