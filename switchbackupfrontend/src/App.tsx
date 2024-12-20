import { useState, useEffect } from 'react';

const App = () => {
  const [switchNames, setSwitchNames] = useState([]);
  const [switchName, setSwitchName] = useState('');
  const [date1, setDate1] = useState('');
  const [date2, setDate2] = useState('');
  const [configDisplay1, setConfigDisplay1] = useState('');
  const [configDisplay2, setConfigDisplay2] = useState('');
  const [compareDisplay, setCompareDisplay] = useState('');
  const [isGetConfigsDisabled, setIsGetConfigsDisabled] = useState(true);
  const [isCompareConfigsDisabled, setIsCompareConfigsDisabled] = useState(true);

  useEffect(() => {
      // Fetch switch names on component mount
      fetch('/api/switch_list')
          .then(response => response.json())
          .then(data => setSwitchNames(data.switch_names))
          .catch(error => console.error('Error fetching switches:', error));
  }, []);

  const validateDateFormat = (date: string) => {
    const regex: RegExp = /^(0[1-9]|1[0-2])-([0-2][0-9]|3[0-1])-\d{4}$/;
    return regex.test(date) || date.toLowerCase() === 'current';
  };

  function convertToMMDDYYYY(dateString: string): string {
    const [year, month, day] = dateString.split("-");
    if (!year || !month || !day) {
        throw new Error("Invalid date format. Expected format: YYYY-MM-DD");
    }
    return `${month}-${day}-${year}`;
  }

  useEffect(() => {
      const isValid = validateDateFormat(date1) && validateDateFormat(date2);
      setIsGetConfigsDisabled(!isValid);
      setIsCompareConfigsDisabled(!isValid);
  }, [date1, date2]);

  const getConfigs = () => {
      setConfigDisplay1('');
      setConfigDisplay2('');
      setIsGetConfigsDisabled(true);

      const newUrl = `/api/get_config?switch_name=${encodeURIComponent(switchName)}&date=${encodeURIComponent(date2)}`;
      fetch(newUrl)
          .then(response => response.json())
          .then(config => {
              setConfigDisplay2(config);
              setIsGetConfigsDisabled(false);
          })
          .catch(error => console.error('Error fetching new config:', error));

      const oldUrl = `/api/get_config?switch_name=${encodeURIComponent(switchName)}&date=${encodeURIComponent(date1)}`;
      fetch(oldUrl)
          .then(response => response.json())
          .then(config => setConfigDisplay1(config))
          .catch(error => console.error('Error fetching old config:', error));
  };

  const compareConfigs = () => {
      setCompareDisplay('');
      setIsCompareConfigsDisabled(true);

      const url = `/api/switch_check?switch_name=${encodeURIComponent(switchName)}&new_date=${encodeURIComponent(date2)}&old_date=${encodeURIComponent(date1)}`;
      fetch(url)
          .then(response => response.json())
          .then(config => {
              setCompareDisplay(config);
              setIsCompareConfigsDisabled(false);
          })
          .catch(error => console.error('Error comparing configs:', error));
  };

  return (
      <div className="p-8 max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold text-center border-b-2 border-green-500 pb-2 mb-4">Config App</h1>

          <div className="mb-4">
              <label htmlFor="switch" className="block text-lg font-medium">Switch:</label>
              <select
                  id="switch"
                  value={switchName}
                  onChange={(e) => setSwitchName(e.target.value)}
                  className="w-full p-2 border rounded"
              >
                  <option value="">Select a switch</option>
                  {switchNames.map(name => (
                      <option key={name} value={name}>{name}</option>
                  ))}
              </select>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                  <label htmlFor="date1" className="block text-lg font-medium">Old Date:</label>
                  <input
                      id="date1"
                      type="date"
                      value={date1}
                      onChange={(e) => setDate1(convertToMMDDYYYY(e.target.value))}
                      className="w-full p-2 border rounded"
                  />
              </div>
              <div>
                  <label htmlFor="date2" className="block text-lg font-medium">New Date:</label>
                  <input
                      id="date2"
                      type="date"
                      value={date2}
                      onChange={(e) => setDate2(convertToMMDDYYYY(e.target.value))}
                      className="w-full p-2 border rounded"
                  />
              </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
              <button
                  onClick={getConfigs}
                  disabled={isGetConfigsDisabled}
                  className={`p-3 rounded font-bold ${isGetConfigsDisabled ? 'bg-gray-400 hover:bg-gray-800' : 'bg-green-500 text-white hover:bg-green-600'}`}
              >
                  Get Configs
              </button>
              <button
                  onClick={compareConfigs}
                  disabled={isCompareConfigsDisabled}
                  className={`p-3 rounded font-bold ${isCompareConfigsDisabled ? 'bg-gray-400 hover:bg-gray-800' : 'bg-blue-500 text-white hover:bg-blue-600'}`}
              >
                  Compare Configs
              </button>
          </div>

          <div className="mb-4">
              <h3 className="text-lg font-bold">Old Config:</h3>
              <pre className="p-2 bg-gray-100 border rounded overflow-auto h-32">{configDisplay1}</pre>
          </div>

          <div className="mb-4">
              <h3 className="text-lg font-bold">New Config:</h3>
              <pre className="p-2 bg-gray-100 border rounded overflow-auto h-32">{configDisplay2}</pre>
          </div>

          <div>
              <h3 className="text-lg font-bold">Comparison:</h3>
              <pre className="p-2 bg-gray-100 border rounded overflow-auto h-32">{compareDisplay}</pre>
          </div>
      </div>
  );
};

export default App;
