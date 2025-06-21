"use client";

import React, { useState, useEffect } from 'react';
import { ChevronDown, LogOut, User } from 'lucide-react';
import { Button } from './ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';

interface UserMenuProps {
  onSignOut: () => void;
}

export const UserMenu: React.FC<UserMenuProps> = ({ onSignOut }) => {
  const [userInfo, setUserInfo] = useState<any>(null);

  useEffect(() => {
    const stored = localStorage.getItem('user_info');
    if (stored) {
      setUserInfo(JSON.parse(stored));
    }
  }, []);

  if (!userInfo) return null;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="flex items-center gap-2">
          <User className="h-4 w-4" />
          <span>{userInfo.full_name}</span>
          <ChevronDown className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel>My Account</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem disabled>
          <span className="text-sm text-muted-foreground">{userInfo.email}</span>
        </DropdownMenuItem>
        <DropdownMenuItem disabled>
          <span className="text-sm">Role: {userInfo.role}</span>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={onSignOut} className="text-red-600">
          <LogOut className="mr-2 h-4 w-4" />
          <span>Sign Out</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};