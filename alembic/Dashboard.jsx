import React from 'react';
import StatsCard from '../components/StatsCard';
import RecentItems from '../components/RecentItems';
import QuickActions from '../components/QuickActions';
import RecentActivity from '../components/RecentActivity';
import { FaBoxOpen, FaCheckCircle, FaClock, FaGift } from 'react-icons/fa';

const Dashboard = ({ openModal }) => {
  const stats = [
    { title: 'Total Items', value: '124', icon: { component: <FaBoxOpen />, color: 'bg-orange-100 text-orange-600' }, trend: 12 },
    { title: 'Items Returned', value: '87', icon: { component: <FaCheckCircle />, color: 'bg-green-100 text-green-600' }, trend: 5 },
    { title: 'Pending Claims', value: '15', icon: { component: <FaClock />, color: 'bg-yellow-100 text-yellow-600' }, trend: -2 },
    { title: 'Rewards Paid', value: 'Ksh 12,450', icon: { component: <FaGift />, color: 'bg-blue-100 text-blue-600' }, trend: 23 },
  ];

  return (
    <main className="dashboard">
      <div className="stats-grid">
        {stats.map((stat, index) => (
          <StatsCard key={index} {...stat} />
        ))}
      </div>
      <div className="content-grid">
        <RecentItems openModal={openModal} />
        <QuickActions openModal={openModal} />
      </div>
      <RecentActivity />
    </main>
  );
};

export default Dashboard;