"use client";
import { useEffect, useState, useRef, useCallback } from "react";

export type Metrics = {
  // System & Performance
  apiResponseTime: number;        // ms
  errorRate: number;              // %
  pageLoadTime: number;           // ms
  activeUsers: number;            // realtime count
  // BU Impact
  conversionRate: number;         // %
  avgEngagement: number;          // seconds
  taskSuccessRate: number;        // %
  retentionRate: number;          // %
  // Time series (last 20 points)
  activeUsersHistory: number[];
  responseTimeHistory: number[];
  // Error breakdown
  errorCount: number;
  successCount: number;
  // Task breakdown
  tasksCompleted: number;
  tasksStarted: number;
  // Engagement by page
  engagementByPage: { page: string; seconds: number }[];
};

const INITIAL: Metrics = {
  apiResponseTime: 245,
  errorRate: 2.1,
  pageLoadTime: 890,
  activeUsers: 14,
  conversionRate: 68.5,
  avgEngagement: 185,
  taskSuccessRate: 91.2,
  retentionRate: 76.3,
  activeUsersHistory: Array.from({ length: 20 }, () => 8 + Math.floor(Math.random() * 12)),
  responseTimeHistory: Array.from({ length: 20 }, () => 200 + Math.floor(Math.random() * 100)),
  errorCount: 3,
  successCount: 142,
  tasksCompleted: 87,
  tasksStarted: 95,
  engagementByPage: [
    { page: "Chat", seconds: 245 },
    { page: "Forms", seconds: 120 },
    { page: "Sign", seconds: 180 },
    { page: "Guide", seconds: 65 },
  ],
};

function jitter(base: number, range: number, min: number, max: number): number {
  const val = base + (Math.random() - 0.5) * range;
  return Math.max(min, Math.min(max, Math.round(val * 10) / 10));
}

function nextMetrics(prev: Metrics): Metrics {
  const activeUsers = Math.max(1, Math.round(jitter(prev.activeUsers, 6, 1, 50)));
  const apiResponseTime = Math.round(jitter(prev.apiResponseTime, 40, 80, 800));
  const errorRate = jitter(prev.errorRate, 1.5, 0, 15);
  const successTotal = prev.successCount + Math.floor(Math.random() * 8);
  const errorTotal = Math.round(successTotal * (errorRate / 100));
  const tasksStarted = prev.tasksStarted + Math.floor(Math.random() * 5);
  const tasksCompleted = Math.min(tasksStarted, prev.tasksCompleted + Math.floor(Math.random() * 4));

  return {
    apiResponseTime,
    errorRate,
    pageLoadTime: Math.round(jitter(prev.pageLoadTime, 50, 300, 2000)),
    activeUsers,
    conversionRate: jitter(prev.conversionRate, 3, 40, 95),
    avgEngagement: Math.round(jitter(prev.avgEngagement, 20, 60, 400)),
    taskSuccessRate: jitter(prev.taskSuccessRate, 2, 70, 99),
    retentionRate: jitter(prev.retentionRate, 2, 50, 95),
    activeUsersHistory: [...prev.activeUsersHistory.slice(1), activeUsers],
    responseTimeHistory: [...prev.responseTimeHistory.slice(1), apiResponseTime],
    errorCount: errorTotal,
    successCount: successTotal,
    tasksCompleted,
    tasksStarted,
    engagementByPage: prev.engagementByPage.map((e) => ({
      ...e,
      seconds: Math.round(jitter(e.seconds, 15, 30, 350)),
    })),
  };
}

export function useMetrics(intervalMs: number = 3000): Metrics {
  const [metrics, setMetrics] = useState<Metrics>(INITIAL);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    timerRef.current = setInterval(() => {
      setMetrics((prev) => nextMetrics(prev));
    }, intervalMs);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [intervalMs]);

  return metrics;
}
