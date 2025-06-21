"use client";

import React from 'react';
import { CalendarIcon } from 'lucide-react';
import { format, subDays } from 'date-fns';
import { Button } from '@/app/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/app/components/ui/select';

interface DateRangePickerProps {
  startDate: Date;
  endDate: Date;
  onDateChange: (start: Date, end: Date) => void;
}

export const DateRangePicker: React.FC<DateRangePickerProps> = ({
  startDate,
  endDate,
  onDateChange,
}) => {
  const presets = [
    { label: 'Last 7 days', days: 7 },
    { label: 'Last 30 days', days: 30 },
    { label: 'Last 90 days', days: 90 },
    { label: 'Last 180 days', days: 180 },
  ];

  const handlePresetChange = (value: string) => {
    const days = parseInt(value);
    const end = new Date();
    const start = subDays(end, days);
    onDateChange(start, end);
  };

  const formatDateRange = () => {
    return `${format(startDate, 'MMM d, yyyy')} - ${format(endDate, 'MMM d, yyyy')}`;
  };

  return (
    <div className="flex items-center space-x-2">
      <Select onValueChange={handlePresetChange}>
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="Select date range" />
        </SelectTrigger>
        <SelectContent>
          {presets.map((preset) => (
            <SelectItem key={preset.days} value={preset.days.toString()}>
              {preset.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      
      <div className="flex items-center space-x-2 text-sm text-muted-foreground">
        <CalendarIcon className="w-4 h-4" />
        <span>{formatDateRange()}</span>
      </div>
    </div>
  );
};