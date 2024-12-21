# gps_demo2.py

import threading
import smbus2
import time

class GPSThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.latest_coords = {'lat': None, 'lon': None}
        self.running = True

        # GPS initialization code
        self.I2C_BUS = 22  # Update this to your correct I2C bus number
        self.DEVICE_ADDRESS = 0x42  # Default I2C address for u-blox GPS modules
        self.bus = smbus2.SMBus(self.I2C_BUS)
        self.buffer = b''
        self.lock = threading.Lock()

    def run(self):
        max_buffer_size = 4096  # Define a reasonable buffer size to prevent overflows
        try:
            while self.running:
                # Read the number of bytes available
                num_bytes = self.read_u16(self.bus, self.DEVICE_ADDRESS, 0xFD)

                if num_bytes == 0:
                    time.sleep(0.1)
                    continue

                # Limit the number of bytes to read
                num_bytes_to_read = min(num_bytes, 512)

                # Read data in chunks
                data = []
                num_bytes_remaining = num_bytes_to_read
                while num_bytes_remaining > 0:
                    to_read = min(num_bytes_remaining, 32)  # I2C buffer limitation
                    try:
                        chunk = self.bus.read_i2c_block_data(self.DEVICE_ADDRESS, 0xFF, to_read)
                        # Check for invalid data patterns and skip if necessary
                        if all(b == 0xFF for b in chunk):
                            num_bytes_remaining -= to_read
                            continue
                        data.extend(chunk)
                    except Exception as e:
                        print(f"Error reading data chunk: {e}")
                        break
                    num_bytes_remaining -= to_read

                if data:
                    # Clean the data
                    data = self.clean_data(bytes(data))
                    self.buffer += data
                    # Limit the buffer size
                    if len(self.buffer) > max_buffer_size:
                        self.buffer = self.buffer[-max_buffer_size:]
                    # Process NMEA sentences
                    self.buffer = self.process_buffer(self.buffer)
                else:
                    pass
                time.sleep(0.1)

        except Exception as e:
            print(f"GPS Thread Exception: {e}")
        finally:
            self.bus.close()

    def read_u16(self, bus, addr, reg):
        """Read an unsigned 16-bit value from the device."""
        try:
            high = bus.read_byte_data(addr, reg)
            low = bus.read_byte_data(addr, reg + 1)
            result = (high << 8) + low
            return result
        except Exception as e:
            print(f"Error reading u16 from register {reg}: {e}")
            return 0

    def clean_data(self, buffer):
        """Remove invalid characters from buffer."""
        cleaned = bytes([b for b in buffer if 32 <= b <= 126 or b in (10, 13)])
        return cleaned

    def process_buffer(self, buffer):
        """Extract NMEA sentences and parse GPS data."""
        lines = buffer.split(b'\r\n')
        buffer = lines[-1]  # Save incomplete line for next read
        for line in lines[:-1]:
            line_str = line.decode('ascii', errors='ignore').strip()
            if not line_str.startswith('$'):
                continue  # Skip lines that do not start with '$'
            if self.verify_checksum(line_str):
                self.parse_nmea_sentence(line_str)
            else:
                pass  # Invalid checksum, ignore
        return buffer

    def verify_checksum(self, nmea_sentence):
        """Verify the checksum of a NMEA sentence."""
        try:
            sentence, checksum = nmea_sentence.split('*')
        except ValueError:
            return False
        sentence = sentence.lstrip('$')
        calculated_checksum = 0
        for char in sentence:
            calculated_checksum ^= ord(char)
        try:
            provided_checksum = int(checksum, 16)
        except ValueError:
            return False
        return calculated_checksum == provided_checksum

    def parse_nmea_sentence(self, sentence):
        """Parse NMEA sentences to extract data."""
        fields = sentence.split(',')

        if sentence.startswith(('$GNGGA', '$GPGGA')):
            self.parse_gga(fields)

        elif sentence.startswith(('$GNRMC', '$GPRMC')):
            self.parse_rmc(fields)

        elif sentence.startswith(('$GNGLL', '$GPGLL')):
            self.parse_gll(fields)

        elif sentence.startswith('$GNVTG', '$GPVTG'):
            self.parse_vtg(fields)

        # You can add more parsing functions if needed

    def parse_gga(self, fields):
        """Parse GGA sentence."""
        if len(fields) >= 6:
            lat_raw = fields[2]
            lat_dir = fields[3]
            lon_raw = fields[4]
            lon_dir = fields[5]
            self.update_coordinates(lat_raw, lat_dir, lon_raw, lon_dir)
    def parse_vtg(self, fields):
       try:
          speed_kph = fields[7]
          with self.lock:
              self.latest_speed = float(speed_kph) if speed_kph else 0.0
          print(f"Speed: {speed_knots} knots, {speed_kph} km/h")
       except (IndexError, ValueError) as e:
          print(f"Error parsing VTG sentence: {e}")

    def get_latest_speed(self):
        with self.lock:
            return self.latest_speed

    def parse_rmc(self, fields):
        """Parse RMC sentence."""
        if len(fields) >= 7:
            lat_raw = fields[3]
            lat_dir = fields[4]
            lon_raw = fields[5]
            lon_dir = fields[6]
            self.update_coordinates(lat_raw, lat_dir, lon_raw, lon_dir)

    def parse_gll(self, fields):
        """Parse GLL sentence."""
        if len(fields) >= 5:
            lat_raw = fields[1]
            lat_dir = fields[2]
            lon_raw = fields[3]
            lon_dir = fields[4]
            self.update_coordinates(lat_raw, lat_dir, lon_raw, lon_dir)

    def update_coordinates(self, lat_raw, lat_dir, lon_raw, lon_dir):
        """Update the latest coordinates."""
        lat = self.nmea_to_decimal(lat_raw, lat_dir)
        lon = self.nmea_to_decimal(lon_raw, lon_dir)
        if lat is not None and lon is not None:
            self.latest_coords['lat'] = lat
            self.latest_coords['lon'] = lon

    def nmea_to_decimal(self, raw_value, direction):
        """Convert NMEA coordinate format to decimal degrees."""
        try:
            if '.' not in raw_value:
                return None
            decimal_pos = raw_value.find('.')
            degrees_length = decimal_pos - 2
            degrees = int(raw_value[:degrees_length])
            minutes = float(raw_value[degrees_length:])
            decimal = degrees + (minutes / 60)
            if direction in ['S', 'W']:
                decimal *= -1
            return decimal
        except Exception:
            return None

    def stop(self):
        """Stop the GPS thread."""
        self.running = False

if __name__ == '__main__':

gps_thread = GPSThread()
gps_thread.start()
try:
while True:
with gps_thread.lock:
lat = gps_thread.latest_coords.get('lat')
lon = gps_thread.latest_coords.get('lon')
print(f"Latitude: {lat}, Longitude: {lon}")
time.sleep(1)
except KeyboardInterrupt:
gps_thread.stop()
gps_thread.join()