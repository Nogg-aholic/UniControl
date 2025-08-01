/**
 * TypeScript declarations for Home Assistant Universal Controller
 */

declare namespace HomeAssistant {
  interface EntityState {
    state: string;
    attributes: Record<string, any>;
    entity_id: string;
    last_changed: string;
    last_updated: string;
    domain: string;
    object_id: string;
    name: string;
  }

  interface Config {
    latitude: number;
    longitude: number;
    elevation: number;
    unit_system: string;
    time_zone: string;
    version: string;
    config_dir: string;
  }

  interface HASS {
    states: Record<string, EntityState>;
    config: Config;
    hacs_repositories: HACS.Repository[];
    hacs_info: HACS.Info;
    hacs_status: HACS.Status;
    callService: (domain: string, service: string, data?: Record<string, any>) => Promise<any>;
  }
}

declare namespace HACS {
  interface Repository {
    name: string;
    description: string;
    installed: boolean;
    available_version: string;
    installed_version: string;
    category: string;
    stars: number;
    topics: string[];
  }

  interface Info {
    version: string;
    dev: boolean;
    debug: boolean;
  }

  interface Status {
    startup: boolean;
    background_task: boolean;
    lovelace_mode: string;
  }

  interface API {
    getRepositories(): Repository[];
    getRepository(name: string): Repository | undefined;
    isInstalled(name: string): boolean;
    install(name: string): Promise<void>;
    uninstall(name: string): Promise<void>;
    update(name: string): Promise<void>;
    getInfo(): Info;
    getStatus(): Status;
  }
}

declare namespace Services {
  interface API {
    call(domain: string, service: string, data?: Record<string, any>): Promise<any>;
    turnOn(entityId: string, data?: Record<string, any>): Promise<any>;
    turnOff(entityId: string, data?: Record<string, any>): Promise<any>;
    toggle(entityId: string, data?: Record<string, any>): Promise<any>;
    notify(message: string, title?: string, data?: Record<string, any>): Promise<any>;
    runScript(scriptId: string, data?: Record<string, any>): Promise<any>;
    triggerAutomation(automationId: string): Promise<any>;
  }
}

declare namespace Utils {
  interface API {
    getEntity(entityId: string): HomeAssistant.EntityState | undefined;
    getEntityState(entityId: string): string | undefined;
    getEntityAttribute(entityId: string, attr: string): any;
    filterEntities(domain: string): string[];
    getEntitiesByDomain(domain: string): Record<string, HomeAssistant.EntityState>;
    isOn(entityId: string): boolean;
    isOff(entityId: string): boolean;
    now(): string;
    timestamp(): number;
    parseNumber(value: any): number;
    parseBoolean(value: any): boolean;
    sum(arr: number[]): number;
    avg(arr: number[]): number;
    min(arr: number[]): number;
    max(arr: number[]): number;
  }
}

declare namespace Console {
  interface API {
    log(...args: any[]): void;
    error(...args: any[]): void;
    warn(...args: any[]): void;
    info(...args: any[]): void;
    debug(...args: any[]): void;
  }
}

declare namespace DateUtils {
  interface API {
    now(): number;
    utc(): string;
    local(): string;
    parse(str: string): Date;
    format(date: Date | string, format?: string): string;
  }
}

// Global variables available in Universal Controller scripts
declare const hass: HomeAssistant.HASS;
declare const states: Record<string, HomeAssistant.EntityState>;
declare const console: Console.API;
declare const Date: DateUtils.API;
declare const Math: Math;
declare const HACS: HACS.API;
declare const services: Services.API;
declare const utils: Utils.API;

// Common patterns and examples
declare namespace Examples {
  /**
   * Get all lights that are currently on
   */
  function getLightsOn(): HomeAssistant.EntityState[];

  /**
   * Calculate average temperature from multiple sensors
   */
  function getAverageTemperature(sensorIds: string[]): number;

  /**
   * Send notification with current weather
   */
  function notifyWeather(): Promise<void>;

  /**
   * Create a simple chart data structure
   */
  function createChartData(entityIds: string[]): ChartData;

  interface ChartData {
    labels: string[];
    datasets: {
      label: string;
      data: number[];
      backgroundColor?: string;
      borderColor?: string;
    }[];
  }
}
