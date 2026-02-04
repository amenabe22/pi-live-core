// Mock types for Operations Center (dispatcher) – no backend yet

export type CallStatus = 'new' | 'emergency' | 'reassigned' | 'unassigned';

export interface DispatchCall {
  id: string;
  status: CallStatus;
  location: string;
  time: string;
  description: string;
}

export type DriverStatus = 'available' | 'busy' | 'on_route' | 'offline' | 'emergency';

export interface DispatchDriver {
  id: string;
  name: string;
  status: DriverStatus;
  location: string;
  lastUpdated: string;
  distance?: string;
  eta?: string;
}

export const MOCK_DISPATCHABLE_CALLS: DispatchCall[] = [
  { id: '99757628', status: 'emergency', location: '2420 SW 27 Ave, MIA', time: '23:45 AM', description: 'Urgent medical request - possible cardiac arrest' },
  { id: '99757629', status: 'new', location: '1500 NW 42 Ave, MIA', time: '2:30 PM', description: 'Wheelchair transport - hospital discharge' },
  { id: '99757630', status: 'reassigned', location: '8800 SW 72 St, MIA', time: '3:15 PM', description: 'Elderly transport - dialysis appointment' },
];

export const MOCK_UNASSIGNED_CALLS: DispatchCall[] = [
  { id: '99757631', status: 'unassigned', location: '1200 Brickell Ave, MIA', time: '4:00 PM', description: 'Airport pickup - accessibility van required' },
  { id: '99757632', status: 'new', location: '701 Brickell Ave, MIA', time: '4:45 PM', description: 'Medical appointment - stretcher vehicle' },
];

export const MOCK_DRIVERS: DispatchDriver[] = [
  { id: 'd1', name: 'William Rivers', status: 'on_route', location: '2400 SW 28 St, Miami', lastUpdated: '5 min ago', distance: '3.0 mi', eta: '15 min' },
  { id: 'd2', name: 'Robert Curtis', status: 'available', location: '2500 SW 27 Ave, Miami', lastUpdated: '2 min ago', distance: '5.0 mi', eta: '20 min' },
  { id: 'd3', name: 'Moya Anderson', status: 'offline', location: '2600 SW 26 Ct, Miami', lastUpdated: '1 hour ago', distance: '—', eta: '—' },
  { id: 'd4', name: 'Mary Johnson', status: 'busy', location: '2700 SW 25 Ave, Miami', lastUpdated: '10 min ago', distance: '2.0 mi', eta: '10 min' },
  { id: 'd5', name: 'Zack Williams', status: 'available', location: '2800 SW 24 St, Miami', lastUpdated: '3 min ago', distance: '1.5 mi', eta: '12 min' },
  { id: 'd6', name: 'Jessica Allen', status: 'on_route', location: '2900 SW 23 Ave, Miami', lastUpdated: '5 min ago', distance: '4.0 mi', eta: '18 min' },
  { id: 'd7', name: 'Robert Wilson', status: 'available', location: '3000 SW 22 St, Miami', lastUpdated: '1 min ago', distance: '2.5 mi', eta: '14 min' },
];

export const MOCK_RECENT_DISPATCHES: DispatchDriver[] = [
  { id: 'd1', name: 'William Rivers', status: 'on_route', location: '2400 SW 28 St, Miami', lastUpdated: '5 min ago' },
  { id: 'd4', name: 'Mary Johnson', status: 'busy', location: '2700 SW 25 Ave, Miami', lastUpdated: '10 min ago' },
  { id: 'd6', name: 'Jessica Allen', status: 'on_route', location: '2900 SW 23 Ave, Miami', lastUpdated: '5 min ago' },
  { id: 'd2', name: 'Robert Curtis', status: 'available', location: '2500 SW 27 Ave, Miami', lastUpdated: '2 min ago' },
  { id: 'd5', name: 'Zack Williams', status: 'available', location: '2800 SW 24 St, Miami', lastUpdated: '3 min ago' },
  { id: 'd7', name: 'Robert Wilson', status: 'available', location: '3000 SW 22 St, Miami', lastUpdated: '1 min ago' },
  { id: 'd3', name: 'Moya Anderson', status: 'offline', location: '2600 SW 26 Ct, Miami', lastUpdated: '1 hour ago' },
];
