import { StatCard } from '@/components';
import { Users, Mail, Shield, UserCheck, UserX } from 'lucide-react';

interface UserStats {
  total: number;
  active: number;
  blocked: number;
  pending: number;
  admin: number;
}

interface Props {
  userStats?: UserStats;
}

export default function UserStatsComponent({ userStats }: Props) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
      <StatCard
        title="Total Users"
        value={userStats?.total}
        subtitle=""
        icon={Users}
        iconBgColor="bg-[#eff6ff]"
        iconColor="text-[#3b82f6]"
      />

      <StatCard
        title=" Active"
        value={userStats?.active}
        subtitle=""
        icon={UserCheck}
        iconBgColor="bg-[#eff6ff]"
        iconColor="text-[#00a63e]"
      />

      <StatCard
        title="Blocked"
        value={userStats?.blocked}
        subtitle=""
        icon={UserX}
        iconBgColor="bg-[#eff6ff]"
        iconColor="text-[#e7000b]"
      />

      <StatCard
        title="Pending"
        value={userStats?.pending}
        subtitle=""
        icon={Mail}
        iconBgColor="bg-[#eff6ff]"
        iconColor="text-[#d97706]"
      />
      <StatCard
        title="Admin"
        value={userStats?.admin}
        subtitle=""
        icon={Shield}
        iconBgColor="bg-[#eff6ff]"
        iconColor="text-[#155dfc]"
      />
    </div>
  );
}
