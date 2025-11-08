// src/hooks/useLatestUsageCO2.js
import { useEffect, useState } from 'react';
import axios from 'axios';

// Supabase-Daten
const SUPABASE_URL = 'https://ywheivlrppourvacbxkz.supabase.co';
const API_KEY      = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl3aGVpdmxycHBvdXJ2YWNieGt6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI0OTc5NzUsImV4cCI6MjA2ODA3Mzk3NX0.mVn0mE2DVnBc5wAdAPivi6CzL4YalS2FUtk2R7h_L8A';                  // ⇽ anon key
const TABLE        = 'usage_phase';
const POLL_MS      = 60_000;   // 60 000 ms = 1 min

export default function useLatestUsageCO2() {
  const [value, setValue] = useState(null);

  useEffect(() => {
    const headers = {
      apikey: API_KEY,
      Authorization: `Bearer ${API_KEY}`
    };

    async function fetchLatest() {
      try {
        const url =
          `${SUPABASE_URL}/rest/v1/${TABLE}` +
          `?select=co2_location_kg` +
          `&order=ts_utc.desc` +
          `&limit=1`;

        const { data } = await axios.get(url, { headers });
        if (Array.isArray(data) && data.length) {
          setValue(Number(data[0].co2_location_kg));
        }
      } catch (err) {
        console.error('Supabase fetch error', err);
      }
    }

    fetchLatest();
    const id = setInterval(fetchLatest, POLL_MS);
    return () => clearInterval(id);
  }, []);

  return value;
}