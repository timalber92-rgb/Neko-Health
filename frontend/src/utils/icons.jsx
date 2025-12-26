/**
 * Professional Medical Icon Library
 * Maps medical concepts to Heroicons for consistent, professional appearance
 */

import {
  HeartIcon,
  BeakerIcon,
  UserIcon,
  BuildingOffice2Icon,
  ClipboardDocumentCheckIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ChartBarIcon,
  DocumentTextIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CalendarIcon,
  UserCircleIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  ChevronDownIcon,
  EyeIcon,
  BoltIcon,
  ShieldCheckIcon,
} from '@heroicons/react/24/outline';

import {
  HeartIcon as HeartIconSolid,
  ExclamationTriangleIcon as ExclamationTriangleIconSolid,
  CheckCircleIcon as CheckCircleIconSolid,
  InformationCircleIcon as InformationCircleIconSolid,
} from '@heroicons/react/24/solid';

// Medical concept icon mapping
export const MedicalIcons = {
  // Main application
  heart: HeartIcon,
  heartSolid: HeartIconSolid,

  // Interventions
  medication: BeakerIcon,
  lifestyle: UserIcon,
  hospital: BuildingOffice2Icon,
  monitoring: EyeIcon,
  clinical: ClipboardDocumentCheckIcon,

  // Alerts and status
  warning: ExclamationTriangleIcon,
  warningSolid: ExclamationTriangleIconSolid,
  info: InformationCircleIcon,
  infoSolid: InformationCircleIconSolid,
  success: CheckCircleIcon,
  successSolid: CheckCircleIconSolid,
  error: XCircleIcon,

  // Analytics
  chart: ChartBarIcon,
  document: DocumentTextIcon,
  trendUp: ArrowTrendingUpIcon,
  trendDown: ArrowTrendingDownIcon,

  // User interface
  calendar: CalendarIcon,
  user: UserCircleIcon,
  settings: Cog6ToothIcon,
  logout: ArrowRightOnRectangleIcon,
  dropdown: ChevronDownIcon,
  shield: ShieldCheckIcon,
  activity: BoltIcon,
};

// Icon wrapper component for consistent sizing
export const Icon = ({ icon: IconComponent, className = '', size = 'md', ...props }) => {
  const sizeClasses = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
    xl: 'w-8 h-8',
  };

  return <IconComponent className={`${sizeClasses[size]} ${className}`} {...props} />;
};

// Action-specific icon components for quick use
export const ActionIcon = ({ action, className = '', size = 'lg' }) => {
  const actionIcons = {
    0: { icon: MedicalIcons.monitoring, color: 'text-info-600' }, // Monitor Only
    1: { icon: MedicalIcons.lifestyle, color: 'text-normal-600' }, // Lifestyle
    2: { icon: MedicalIcons.medication, color: 'text-clinical-600' }, // Single Med
    3: { icon: MedicalIcons.clinical, color: 'text-warning-600' }, // Combination
    4: { icon: MedicalIcons.hospital, color: 'text-critical-600' }, // Intensive
  };

  const config = actionIcons[action] || actionIcons[0];
  return <Icon icon={config.icon} size={size} className={`${config.color} ${className}`} />;
};

// Risk level icon component
export const RiskIcon = ({ level, className = '', size = 'md', solid = false }) => {
  const riskConfig = {
    low: {
      icon: solid ? MedicalIcons.successSolid : MedicalIcons.success,
      color: 'text-normal-600',
    },
    moderate: {
      icon: solid ? MedicalIcons.warningSolid : MedicalIcons.warning,
      color: 'text-warning-600',
    },
    high: {
      icon: solid ? MedicalIcons.warningSolid : MedicalIcons.warning,
      color: 'text-critical-600',
    },
  };

  const config = riskConfig[level] || riskConfig.moderate;
  return <Icon icon={config.icon} size={size} className={`${config.color} ${className}`} />;
};

export default MedicalIcons;
