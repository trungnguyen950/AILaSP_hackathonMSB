"use client";
import { useEffect, useState, useRef } from "react";

export type Metrics = {
  // ═══ KPI TỔNG QUAN (realtime) ═══
  totalDossiers: number;
  readyCount: number;
  missingCount: number;
  reviewCount: number;
  readyRate: number;

  // ═══ HIỆU QUẢ VẬN HÀNH ═══
  avgHandlingTime: number;
  returnRate: number;
  handlingTimeHistory: number[];
  activeSessions: number;
  activeSessionsHistory: number[];

  // ═══ GIÁ TRỊ KINH DOANH (AEV) ═══
  estimatedSavings: number;
  savingsToday: number;
  rmTimeSaved: number;

  // ═══ PHÂN KHÚC KHÁCH HÀNG ═══
  segmentVolume: { segment: string; count: number; color: string }[];

  // ═══ SIGNING FUNNEL ═══
  signFunnel: { stage: string; count: number; color: string }[];
  signSuccessRate: number;
  totalSigned: number;

  // ═══ FORM USAGE ═══
  formUsageBySource: { source: string; count: number; color: string }[];
  formUsage: { code: string; name: string; count: number; source: string }[];

  // ═══ DAILY SIGN TREND ═══
  signTrend: { day: string; signed: number; failed: number }[];

  // ═══ RM PERFORMANCE ═══
  rmPerformance: { name: string; dossiers: number; readyRate: number; color: string }[];

  // ═══ KHÁCH HÀNG ═══
  npsScore: number;
  csatScore: number;
  returningCustomers: number;
  returnCustomerRate: number;

  // ═══ FDI STRATEGIC ═══
  fdiServed: number;
  fdiBilingualForms: number;
  fdiSatisfaction: number;

  // ═══ KỲ TRƯỚC (delta) ═══
  prevReadyRate: number;
  prevAvgHandlingTime: number;
  prevReturnRate: number;
  prevNps: number;
};

const INITIAL: Metrics = {
  totalDossiers: 1247,
  readyCount: 1083,
  missingCount: 112,
  reviewCount: 52,
  readyRate: 86.8,
  avgHandlingTime: 12.5,
  returnRate: 9.0,
  handlingTimeHistory: Array.from({ length: 20 }, () => 10 + Math.random() * 6),
  activeSessions: 14,
  activeSessionsHistory: Array.from({ length: 20 }, () => 8 + Math.floor(Math.random() * 12)),
  estimatedSavings: 174_580_000,
  savingsToday: 12_600_000,
  rmTimeSaved: 682,
  segmentVolume: [
    { segment: "KH Doanh nghiệp", count: 892, color: "#0B1F3A" },
    { segment: "KH FDI", count: 156, color: "#7c3aed" },
    { segment: "KH Cá nhân", count: 199, color: "#E30613" },
  ],
  signFunnel: [
    { stage: "Form Selected", count: 320, color: "#1757A6" },
    { stage: "Data Collected", count: 285, color: "#7c3aed" },
    { stage: "QC Passed", count: 251, color: "#F59E0B" },
    { stage: "Signed", count: 218, color: "#00A676" },
  ],
  signSuccessRate: 68.1,
  totalSigned: 218,
  formUsageBySource: [
    { source: "Chat (persona)", count: 198, color: "#E30613" },
    { source: "Forms (AI Fill)", count: 87, color: "#7c3aed" },
    { source: "Forms (download)", count: 45, color: "#1757A6" },
  ],
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
  signTrend: Array.from({ length: 14 }, (_, i) => ({
    day: `Day ${i + 1}`,
    signed: 8 + Math.floor(Math.random() * 18),
    failed: Math.floor(Math.random() * 4),
  })),
  rmPerformance: [
    { name: "Nguyễn Thị Lan", dossiers: 87, readyRate: 91, color: "#00A676" },
    { name: "Trần Hoàng Nam", dossiers: 72, readyRate: 88, color: "#1757A6" },
    { name: "Lê Minh Đức", dossiers: 65, readyRate: 85, color: "#7c3aed" },
    { name: "Phạm Thu Hà", dossiers: 58, readyRate: 89, color: "#E30613" },
    { name: "Võ Thanh Tùng", dossiers: 51, readyRate: 83, color: "#F59E0B" },
  ],
  npsScore: 42,
  csatScore: 4.3,
  returningCustomers: 318,
  returnCustomerRate: 25.5,
  fdiServed: 156,
  fdiBilingualForms: 89,
  fdiSatisfaction: 4.6,
  prevReadyRate: 82.1,
  prevAvgHandlingTime: 14.8,
  prevReturnRate: 12.5,
  prevNps: 35,
};

function jitter(base: number, range: number, min: number, max: number): number {
  const val = base + (Math.random() - 0.5) * range;
  return Math.max(min, Math.min(max, Math.round(val * 10) / 10));
}

function nextMetrics(prev: Metrics): Metrics {
  const newDossiers = Math.floor(Math.random() * 3);
  const totalDossiers = prev.totalDossiers + newDossiers;
  const readyRate = jitter(prev.readyRate, 2, 75, 95);
  const readyCount = Math.round((readyRate / 100) * totalDossiers);
  const missingCount = Math.round(((100 - readyRate) / 100) * totalDossiers * 0.68);
  const reviewCount = totalDossiers - readyCount - missingCount;
  const avgHandlingTime = jitter(prev.avgHandlingTime, 1.2, 8, 20);
  const returnRate = jitter(prev.returnRate, 0.8, 5, 15);
  const activeSessions = Math.max(1, Math.round(jitter(prev.activeSessions, 6, 1, 50)));
  const savingsPerTick = Math.round(prev.savingsToday / 288);
  const estimatedSavings = prev.estimatedSavings + savingsPerTick;
  const savingsToday = prev.savingsToday + Math.floor(Math.random() * 500_000);
  const rmTimeSaved = prev.rmTimeSaved + (Math.random() > 0.5 ? 1 : 0);
  const npsScore = jitter(prev.npsScore, 2, 20, 70);
  const csatScore = jitter(prev.csatScore, 0.15, 3.5, 5.0);
  const fdiServed = prev.fdiServed + (Math.random() > 0.7 ? 1 : 0);
  const fdiBilingualForms = prev.fdiBilingualForms + (Math.random() > 0.8 ? 1 : 0);
  const fdiSatisfaction = jitter(prev.fdiSatisfaction, 0.1, 4.0, 5.0);
  const returningCustomers = prev.returningCustomers + (Math.random() > 0.6 ? 1 : 0);
  const returnCustomerRate = jitter(prev.returnCustomerRate, 1.5, 15, 40);

  return {
    totalDossiers,
    readyCount,
    missingCount,
    reviewCount,
    readyRate,
    avgHandlingTime,
    returnRate,
    handlingTimeHistory: [...prev.handlingTimeHistory.slice(1), avgHandlingTime],
    activeSessions,
    activeSessionsHistory: [...prev.activeSessionsHistory.slice(1), activeSessions],
    estimatedSavings,
    savingsToday,
    rmTimeSaved,
    segmentVolume: prev.segmentVolume.map((s) => ({
      ...s,
      count: s.count + (Math.random() > 0.6 ? 1 : 0),
    })),
    signFunnel: prev.signFunnel.map((s) => ({
      ...s,
      count: s.count + Math.floor(Math.random() * 3),
    })),
    signSuccessRate: jitter(prev.signSuccessRate, 1.5, 55, 85),
    totalSigned: prev.totalSigned + (Math.random() > 0.6 ? 1 : 0),
    formUsageBySource: prev.formUsageBySource.map((s) => ({
      ...s,
      count: s.count + (Math.random() > 0.7 ? 1 : 0),
    })),
    formUsage: prev.formUsage.map((f) => ({
      ...f,
      count: f.count + (Math.random() > 0.75 ? 1 : 0),
    })),
    signTrend: [
      ...prev.signTrend.slice(1),
      {
        day: `Day ${prev.signTrend.length + 1}`,
        signed: 8 + Math.floor(Math.random() * 18),
        failed: Math.floor(Math.random() * 4),
      },
    ],
    rmPerformance: prev.rmPerformance.map((r) => ({
      ...r,
      dossiers: r.dossiers + (Math.random() > 0.7 ? 1 : 0),
      readyRate: jitter(r.readyRate, 1, 75, 95),
    })),
    npsScore,
    csatScore,
    returningCustomers,
    returnCustomerRate,
    fdiServed,
    fdiBilingualForms,
    fdiSatisfaction,
    prevReadyRate: prev.prevReadyRate,
    prevAvgHandlingTime: prev.prevAvgHandlingTime,
    prevReturnRate: prev.prevReturnRate,
    prevNps: prev.prevNps,
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
