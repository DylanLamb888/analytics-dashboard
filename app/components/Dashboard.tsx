"use client";

import React, { useState, useEffect } from 'react';
import { FileUpload } from './FileUpload';
import { DateRangePicker } from './DateRangePicker';
import { MetricsCard } from './MetricsCard';
import { SalesChart } from './charts/SalesChart';
import { TopProductsChart } from './charts/TopProductsChart';
import { Button } from './ui/button';
import { UserMenu } from './UserMenu';
import { metricsApi, exportApi } from '@/app/lib/api';
import { subDays } from 'date-fns';
import { 
  DollarSign, 
  ShoppingCart, 
  Package, 
  Users, 
  Download,
  RefreshCw 
} from 'lucide-react';
import { motion } from 'framer-motion';

interface DashboardProps {
  onSignOut: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onSignOut }) => {
  const [loading, setLoading] = useState(true);
  const [hasData, setHasData] = useState(false);
  const [startDate, setStartDate] = useState(subDays(new Date(), 30));
  const [endDate, setEndDate] = useState(new Date());
  const [metrics, setMetrics] = useState<any>(null);
  const [exporting, setExporting] = useState(false);

  const fetchMetrics = async () => {
    setLoading(true);
    try {
      const data = await metricsApi.getDashboardMetrics({
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
      });
      setMetrics(data);
      setHasData(true);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
      setHasData(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Reset state on mount for clean demo
    setHasData(false);
    setMetrics(null);
    fetchMetrics();
  }, []);

  useEffect(() => {
    fetchMetrics();
  }, [startDate, endDate]);

  const handleDateChange = (start: Date, end: Date) => {
    setStartDate(start);
    setEndDate(end);
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      await exportApi.exportToExcel({
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
      });
    } catch (error) {
      console.error('Failed to export:', error);
    } finally {
      setExporting(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  if (!hasData && !loading) {
    return (
      <div className="min-h-screen bg-background p-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-7xl mx-auto"
        >
          <h1 className="text-3xl font-bold mb-8">Order Analytics Dashboard</h1>
          <div className="flex flex-col items-center justify-center space-y-6 mt-16">
            <h2 className="text-xl font-medium text-muted-foreground">
              No data available. Please upload a CSV file to get started.
            </h2>
            <FileUpload onUploadSuccess={fetchMetrics} />
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-7xl mx-auto space-y-8"
      >
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
          <h1 className="text-3xl font-bold">Order Analytics Dashboard</h1>
          <div className="flex items-center space-x-4">
            <DateRangePicker
              startDate={startDate}
              endDate={endDate}
              onDateChange={handleDateChange}
            />
            <Button
              variant="outline"
              size="icon"
              onClick={fetchMetrics}
              disabled={loading}
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </Button>
            <Button
              onClick={handleExport}
              disabled={exporting || !hasData}
            >
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
            <UserMenu onSignOut={onSignOut} />
          </div>
        </div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricsCard
            title="Total Revenue"
            value={formatCurrency(metrics?.sales_metrics?.total_revenue || 0)}
            description="Total sales revenue"
            icon={<DollarSign className="w-4 h-4 text-muted-foreground" />}
            loading={loading}
          />
          <MetricsCard
            title="Total Orders"
            value={metrics?.sales_metrics?.total_orders || 0}
            description="Number of orders"
            icon={<ShoppingCart className="w-4 h-4 text-muted-foreground" />}
            loading={loading}
          />
          <MetricsCard
            title="Items Sold"
            value={metrics?.sales_metrics?.total_items_sold || 0}
            description="Total units sold"
            icon={<Package className="w-4 h-4 text-muted-foreground" />}
            loading={loading}
          />
          <MetricsCard
            title="Unique Customers"
            value={metrics?.sales_metrics?.unique_customers || 0}
            description="Individual customers"
            icon={<Users className="w-4 h-4 text-muted-foreground" />}
            loading={loading}
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SalesChart
            data={metrics?.time_series || []}
            loading={loading}
          />
          <TopProductsChart
            data={metrics?.top_products || []}
            loading={loading}
          />
        </div>

        {/* Upload Section */}
        <div className="pt-8">
          <h2 className="text-xl font-semibold mb-4">Upload New Data</h2>
          <FileUpload onUploadSuccess={fetchMetrics} />
        </div>
      </motion.div>
    </div>
  );
};