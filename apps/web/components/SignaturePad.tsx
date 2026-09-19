"use client";
import { useRef, useEffect, useImperativeHandle, forwardRef, useCallback } from "react";

export type SignaturePadRef = {
  isEmpty: () => boolean;
  toDataURL: () => string;
  clear: () => void;
};

type Point = { x: number; y: number };

export const SignaturePad = forwardRef<SignaturePadRef, { className?: string }>(
  ({ className = "" }, ref) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const drawingRef = useRef(false);
    const pointsRef = useRef<Point[]>([]);
    const hasSignedRef = useRef(false);

    const getCtx = useCallback(() => {
      const canvas = canvasRef.current;
      if (!canvas) return null;
      const ctx = canvas.getContext("2d");
      if (!ctx) return null;
      return { canvas, ctx };
    }, []);

    const setupCanvas = useCallback(() => {
      const result = getCtx();
      if (!result) return;
      const { canvas, ctx } = result;
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
      ctx.lineWidth = 2.5;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      ctx.strokeStyle = "#0b1f3a";
    }, [getCtx]);

    useEffect(() => {
      setupCanvas();
      const onResize = () => {
        const data = canvasRef.current?.toDataURL();
        setupCanvas();
        if (data && hasSignedRef.current) {
          const img = new Image();
          img.onload = () => {
            const ctx = canvasRef.current?.getContext("2d");
            ctx?.drawImage(img, 0, 0, canvasRef.current!.getBoundingClientRect().width, canvasRef.current!.getBoundingClientRect().height);
          };
          img.src = data;
        }
      };
      window.addEventListener("resize", onResize);
      return () => window.removeEventListener("resize", onResize);
    }, [setupCanvas]);

    const getPos = (e: React.MouseEvent | React.TouchEvent): Point => {
      const canvas = canvasRef.current!;
      const rect = canvas.getBoundingClientRect();
      if ("touches" in e) {
        return { x: e.touches[0].clientX - rect.left, y: e.touches[0].clientY - rect.top };
      }
      return { x: e.clientX - rect.left, y: e.clientY - rect.top };
    };

    const startDraw = (e: React.MouseEvent | React.TouchEvent) => {
      e.preventDefault();
      drawingRef.current = true;
      const p = getPos(e);
      pointsRef.current = [p];
    };

    const draw = (e: React.MouseEvent | React.TouchEvent) => {
      if (!drawingRef.current) return;
      e.preventDefault();
      const result = getCtx();
      if (!result) return;
      const { ctx } = result;
      const p = getPos(e);
      const prev = pointsRef.current[pointsRef.current.length - 1];
      ctx.beginPath();
      ctx.moveTo(prev.x, prev.y);
      ctx.lineTo(p.x, p.y);
      ctx.stroke();
      pointsRef.current.push(p);
      hasSignedRef.current = true;
    };

    const stopDraw = () => {
      drawingRef.current = false;
    };

    useImperativeHandle(ref, () => ({
      isEmpty: () => !hasSignedRef.current,
      toDataURL: () => canvasRef.current?.toDataURL("image/png") || "",
      clear: () => {
        const result = getCtx();
        if (!result) return;
        const { canvas, ctx } = result;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        hasSignedRef.current = false;
      },
    }));

    return (
      <canvas
        ref={canvasRef}
        className={`block w-full touch-none rounded-btn border-2 border-dashed border-ink-200 bg-white cursor-crosshair ${className}`}
        style={{ height: 180 }}
        onMouseDown={startDraw}
        onMouseMove={draw}
        onMouseUp={stopDraw}
        onMouseLeave={stopDraw}
        onTouchStart={startDraw}
        onTouchMove={draw}
        onTouchEnd={stopDraw}
        aria-label="Signature pad — draw your signature"
        role="img"
      />
    );
  }
);

SignaturePad.displayName = "SignaturePad";
