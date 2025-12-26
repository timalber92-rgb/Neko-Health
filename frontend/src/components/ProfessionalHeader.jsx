/**
 * ProfessionalHeader Component
 *
 * Enterprise-grade header for clinical applications
 * Features: App branding, facility context, user profile
 */

import { useState } from 'react';
import { Icon, MedicalIcons } from '../utils/icons.jsx';

export default function ProfessionalHeader() {
  const [showUserMenu, setShowUserMenu] = useState(false);

  // Mock user data - in production this would come from auth context
  const user = {
    name: 'Dr. Sarah Johnson',
    role: 'Cardiologist',
    facility: 'University Medical Center',
    department: 'Cardiology Department',
  };

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left: Application branding */}
          <div className="flex items-center gap-3">
            <Icon
              icon={MedicalIcons.heartSolid}
              size="lg"
              className="text-critical-600"
              aria-hidden="true"
            />
            <div>
              <h1 className="text-lg font-semibold text-gray-900">CardioRisk Assessment</h1>
              <p className="text-xs text-gray-600">Clinical Decision Support System</p>
            </div>
          </div>

          {/* Center: Facility context */}
          <div className="hidden md:flex items-center gap-2 text-sm">
            <Icon
              icon={MedicalIcons.hospital}
              size="sm"
              className="text-gray-500"
              aria-hidden="true"
            />
            <div className="text-center">
              <div className="font-medium text-gray-700">{user.facility}</div>
              <div className="text-xs text-gray-500">{user.department}</div>
            </div>
          </div>

          {/* Right: User profile */}
          <div className="flex items-center gap-4">
            {/* User menu */}
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-2 px-3 py-2 rounded hover:bg-gray-100 transition-colors"
                aria-expanded={showUserMenu}
                aria-haspopup="true"
              >
                <Icon
                  icon={MedicalIcons.user}
                  size="md"
                  className="text-gray-600"
                  aria-hidden="true"
                />
                <div className="hidden sm:block text-left">
                  <div className="text-sm font-medium text-gray-900">{user.name}</div>
                  <div className="text-xs text-gray-600">{user.role}</div>
                </div>
                <Icon
                  icon={MedicalIcons.dropdown}
                  size="sm"
                  className={`text-gray-500 transition-transform ${showUserMenu ? 'rotate-180' : ''}`}
                  aria-hidden="true"
                />
              </button>

              {/* Dropdown menu */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-56 bg-white rounded border border-gray-200 shadow-lg z-50">
                  <div className="p-3 border-b border-gray-200">
                    <div className="font-medium text-gray-900">{user.name}</div>
                    <div className="text-sm text-gray-600">{user.role}</div>
                    <div className="text-xs text-gray-500 mt-1">{user.facility}</div>
                  </div>
                  <div className="py-1">
                    <button className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors">
                      <Icon icon={MedicalIcons.settings} size="sm" className="text-gray-500" />
                      Settings
                    </button>
                    <button className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors">
                      <Icon icon={MedicalIcons.logout} size="sm" className="text-gray-500" />
                      Sign Out
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Close dropdown when clicking outside */}
      {showUserMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowUserMenu(false)}
          aria-hidden="true"
        />
      )}
    </header>
  );
}
