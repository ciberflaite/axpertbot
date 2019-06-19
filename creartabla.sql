CREATE  TABLE datos(
	    id SERIAL ,
	    grid_voltage float(2) NULL,
	    grid_frequency float(2) NULL,
	    ac_output_voltage float(2) NULL,
	   ac_output_frequency float(2) NULL,
	   ac_output_aparent_power SMALLINT NULL,
	   ac_output_active_power SMALLINT NULL,
	   output_load_percent SMALLINT NULL,
	   bus_voltage SMALLINT NULL,
	   battery_voltage float(2) NULL,
	   battery_chraging_current SMALLINT NULL, 
	   battery_capacity SMALLINT NULL,
	   inverter_head_sync_temperature SMALLINT NULL,
	   pv_input_current_for_battery SMALLINT NULL,
	   pv_input_voltage  float(2) NULL,
	   battery_voltage_from_scc float(2) NULL,
	   battery_discharge_current INT NULL,
	   device_status VARCHAR(255) NULL,
	   created_on TIMESTAMPTZ NOT NULL DEFAULT DATE_TRUNC('seconds', NOW())
);




