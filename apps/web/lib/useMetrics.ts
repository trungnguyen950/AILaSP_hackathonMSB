"use client";
import { useEffect, useState, useRef, useCallback } from "react";

export type Metrics = {
  // System & Performance
  apiResponseTime: number;
  errorRate: number;
  pageLoadTime: number;
  activeUsers: number;
  // BU Impact
  conversionRate: number;
  avgEngagement: number;
  taskSuccessRate: number;
  retentionRate: number;
  // Time series
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
  // BA: Signing funnel
  signFunnel: { stage: string; count: number; color: string }[];
  signSuccessRate: number;
  totalSigned: number;
  // BA: Form usage by source
  formUsageBySource: { source: string; count: number; color: string }[];
  // BA: Most used forms (top 9)
  formUsage: { code: string; name: string; count: number; source: string }[];
  // BA: Sign trend (last 14 days)
  signTrend: { day: string; signed: number; failed: number }[];
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
  // BA: Signing funnel
  signFunnel: [
    { stage: "Form Selected", count: 320, color: "#1757A6" },
    { stage: "Data Collected", count: 285, color: "#7c3aed" },
    { stage: "QC Passed", count: 251, color: "#F59E0B" },
    { stage: "Signed", count: 218, color: "#00A676" },
  ],
  signSuccessRate: 68.1,
  totalSigned: 218,
  // BA: Form usage by source
  formUsageBySource: [
    { source: "Chat (persona)", count: 198, color: "#E30613" },
    { source: "Forms (AI Fill)", count: 87, color: "#7c3aed" },
    { source: "Forms (download)", count: 45, color: "#1757A6" },
  ],
  // BA: Most used forms
  formUsage: [
    { code: "MSB-EBANK-01", name: "Đăng ký bổ sung người dùng eBank", count: 72, source: "Chat" },
    { code: "MSB-EBANK-01-FDI", name: "Bổ sung eBank — FDI (Song ngữ)", count: 38, source: "Chat" },
    { code: "MSB-DS-04", name: "Đăng ký/thay đổi chữ ký số", count: 54, source: "Chat" },
    { code: "MSB-ETAX-03", name: "Đăng ký tài khoản nộp thuế điện tử", count: 41, source: "Chat" },
    { code: "MSB-AC-05", name: "Thay đổi thông tin DN & người đại diện", count: 35, source: "Chat" },
    { code: "MSB-EBANK-06", name: "Thay đổi hạn mức & phê duyệt eBank", count: 28, source: "Forms" },
    { code: "MSB-IB-02", name: "Đăng ký Internet Banking (cá nhân)", count: 22, source: "Forms" },
    { code: "MSB-AC-08", name: "Thay đổi thông tin liên hệ", count: 18, source: "Forms" },
    { code: "MSB-EBANK-07", name: "Khóa/mở khóa dịch vụ eBank", count: 12, source: "Forms" },
  ],
  // BA: Sign trend (last 14 days)
  signTrend: Array.from({ length: 14 }, (_, i) => {
    const day = `Day ${i + 1}`;
    const signed = 8 + Math.floor(Math.random() * 18);
    return { day, signed, failed: Math.floor(Math.random() * 4) };
  }),
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
    // BA: Sign funnel — slight growth
    signFunnel: prev.signFunnel.map((s) => ({
      ...s,
      count: s.count + Math.floor(Math.random() * 3),
    })),
    signSuccessRate: jitter(prev.signSuccessRate, 1.5, 55, 85),
    totalSigned: prev.totalSigned + (Math.random() > 0.6 ? 1 : 0),
    // BA: Form usage by source — slow growth
    formUsageBySource: prev.formUsageBySource.map((s) => ({
      ...s,
      count: s.count + (Math.random() > 0.7 ? 1 : 0),
    })),
    // BA: Form usage — occasional new usage
    formUsage: prev.formUsage.map((f) => ({
      ...f,
      count: f.count + (Math.random() > 0.75 ? 1 : 0),
    })),
    // BA: Sign trend — shift window + add new day
    signTrend: [
      ...prev.signTrend.slice(1),
      {
        day: `Day ${prev.signTrend.length + 1}`,
        signed: 8 + Math.floor(Math.random() * 18),
        failed: Math.floor(Math.random() * 4),
      },
    ],
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
