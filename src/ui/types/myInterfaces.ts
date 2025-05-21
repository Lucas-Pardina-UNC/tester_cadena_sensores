export interface Slave {
    slave_id: number;
    sensor_id: string;
    sensor_type: string;
  }
  
export interface Chain {
    id: string;
    chain_port: string;
    baudrate: number;
    bytesize: number;
    parity: string;
    stopbits: number;
    timeout: number;
    chain_protocol: string;
    chain_available_slaves: Slave[];
    result_columns: string;
    fetchChainsData: (projectFolder: string) => Promise<void>;
}
