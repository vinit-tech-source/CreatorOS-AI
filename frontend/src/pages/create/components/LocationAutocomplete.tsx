import { useState, useEffect, useRef, useCallback } from 'react';
import { MapPin, X, Navigation, Check } from 'lucide-react';
import styles from './LocationAutocomplete.module.css';

export interface LocationSuggestion {
  id: string;
  name: string;
  subtitle: string;
  fullName: string;
  type?: string;
}

interface LocationAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onClear: () => void;
  placeholder?: string;
  autoFocus?: boolean;
}

// Popular locations instant dictionary for 0ms immediate feedback
const POPULAR_LOCATIONS: LocationSuggestion[] = [
  { id: 'pune', name: 'Pune', subtitle: 'Maharashtra, India', fullName: 'Pune, Maharashtra, India', type: 'city' },
  { id: 'mumbai', name: 'Mumbai', subtitle: 'Maharashtra, India', fullName: 'Mumbai, Maharashtra, India', type: 'city' },
  { id: 'delhi', name: 'New Delhi', subtitle: 'Delhi, India', fullName: 'New Delhi, Delhi, India', type: 'city' },
  { id: 'bengaluru', name: 'Bengaluru', subtitle: 'Karnataka, India', fullName: 'Bengaluru, Karnataka, India', type: 'city' },
  { id: 'hyderabad', name: 'Hyderabad', subtitle: 'Telangana, India', fullName: 'Hyderabad, Telangana, India', type: 'city' },
  { id: 'chennai', name: 'Chennai', subtitle: 'Tamil Nadu, India', fullName: 'Chennai, Tamil Nadu, India', type: 'city' },
  { id: 'kolkata', name: 'Kolkata', subtitle: 'West Bengal, India', fullName: 'Kolkata, West Bengal, India', type: 'city' },
  { id: 'ahmedabad', name: 'Ahmedabad', subtitle: 'Gujarat, India', fullName: 'Ahmedabad, Gujarat, India', type: 'city' },
  { id: 'goa', name: 'Goa', subtitle: 'India', fullName: 'Goa, India', type: 'state' },
  { id: 'jaipur', name: 'Jaipur', subtitle: 'Rajasthan, India', fullName: 'Jaipur, Rajasthan, India', type: 'city' },
  { id: 'ny', name: 'New York', subtitle: 'New York, United States', fullName: 'New York, NY, USA', type: 'city' },
  { id: 'sf', name: 'San Francisco', subtitle: 'California, United States', fullName: 'San Francisco, CA, USA', type: 'city' },
  { id: 'la', name: 'Los Angeles', subtitle: 'California, United States', fullName: 'Los Angeles, CA, USA', type: 'city' },
  { id: 'london', name: 'London', subtitle: 'United Kingdom', fullName: 'London, United Kingdom', type: 'city' },
  { id: 'dubai', name: 'Dubai', subtitle: 'United Arab Emirates', fullName: 'Dubai, UAE', type: 'city' },
  { id: 'singapore', name: 'Singapore', subtitle: 'Singapore', fullName: 'Singapore', type: 'city' },
  { id: 'tokyo', name: 'Tokyo', subtitle: 'Japan', fullName: 'Tokyo, Japan', type: 'city' },
  { id: 'paris', name: 'Paris', subtitle: 'France', fullName: 'Paris, France', type: 'city' },
  { id: 'toronto', name: 'Toronto', subtitle: 'Ontario, Canada', fullName: 'Toronto, Canada', type: 'city' },
  { id: 'sydney', name: 'Sydney', subtitle: 'New South Wales, Australia', fullName: 'Sydney, Australia', type: 'city' },
];

export function LocationAutocomplete({
  value,
  onChange,
  onClear,
  placeholder = 'Search location (e.g. Pune, New York)…',
  autoFocus = true,
}: LocationAutocompleteProps) {
  const [query, setQuery] = useState(value);
  const [suggestions, setSuggestions] = useState<LocationSuggestion[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceTimer = useRef<any>(null);

  // Sync internal query if parent value changes externally
  useEffect(() => {
    setQuery(value);
  }, [value]);

  // Click outside listener to dismiss dropdown
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch suggestions from Photon API
  const fetchSuggestions = useCallback(async (q: string) => {
    if (!q || q.trim().length < 2) {
      setSuggestions([]);
      setIsOpen(false);
      return;
    }

    const trimmed = q.trim().toLowerCase();

    // Instant local matches first
    const localMatches = POPULAR_LOCATIONS.filter(
      loc => loc.name.toLowerCase().includes(trimmed) || loc.subtitle.toLowerCase().includes(trimmed)
    );

    if (localMatches.length > 0) {
      setSuggestions(localMatches);
      setIsOpen(true);
    }

    setIsLoading(true);

    try {
      const res = await fetch(`https://photon.komoot.io/api/?q=${encodeURIComponent(trimmed)}&limit=6`);
      if (!res.ok) throw new Error('Network error');
      const data = await res.json();

      if (data && Array.isArray(data.features)) {
        const parsed: LocationSuggestion[] = data.features.map((f: any, i: number) => {
          const p = f.properties || {};
          const name = p.name || 'Unknown';
          const subtitleParts = [
            p.district,
            p.city && p.city !== name ? p.city : null,
            p.state,
            p.country
          ].filter(Boolean);
          const subtitle = subtitleParts.join(', ');
          const fullName = subtitle ? `${name}, ${subtitle}` : name;

          return {
            id: `${p.osm_id || i}-${name}`,
            name,
            subtitle,
            fullName,
            type: p.type || p.osm_value || 'location'
          };
        });

        // Deduplicate by fullName
        const seen = new Set<string>();
        const unique = parsed.filter(item => {
          if (seen.has(item.fullName.toLowerCase())) return false;
          seen.add(item.fullName.toLowerCase());
          return true;
        });

        if (unique.length > 0) {
          setSuggestions(unique);
          setIsOpen(true);
        } else if (localMatches.length === 0) {
          setSuggestions([]);
          setIsOpen(true);
        }
      }
    } catch (err) {
      console.warn('Location search fallback to local dataset:', err);
      if (localMatches.length > 0) {
        setSuggestions(localMatches);
        setIsOpen(true);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const nextVal = e.target.value;
    setQuery(nextVal);
    setSelectedIndex(-1);

    if (debounceTimer.current) clearTimeout(debounceTimer.current);

    if (!nextVal.trim()) {
      setSuggestions([]);
      setIsOpen(false);
      onChange('');
      return;
    }

    debounceTimer.current = setTimeout(() => {
      fetchSuggestions(nextVal);
    }, 250);
  };

  const handleSelect = (item: LocationSuggestion) => {
    setQuery(item.fullName);
    onChange(item.fullName);
    setIsOpen(false);
    setSuggestions([]);
  };

  const handleClear = () => {
    setQuery('');
    onChange('');
    setSuggestions([]);
    setIsOpen(false);
    onClear();
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen || suggestions.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => (prev < suggestions.length - 1 ? prev + 1 : 0));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => (prev > 0 ? prev - 1 : suggestions.length - 1));
    } else if (e.key === 'Enter') {
      if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
        e.preventDefault();
        handleSelect(suggestions[selectedIndex]);
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  return (
    <div className={styles.container} ref={containerRef}>
      <div className={styles.inputRow}>
        <MapPin size={15} className={styles.icon} />
        <input
          ref={inputRef}
          className={styles.input}
          placeholder={placeholder}
          value={query}
          onChange={handleInputChange}
          onFocus={() => {
            if (query.trim().length >= 2) {
              fetchSuggestions(query);
            }
          }}
          onKeyDown={handleKeyDown}
          autoFocus={autoFocus}
        />
        {isLoading && <div className={styles.spinner} />}
        {query && !isLoading && (
          <button type="button" className={styles.clearBtn} onClick={handleClear} title="Clear location">
            <X size={14} />
          </button>
        )}
      </div>

      {/* Dropdown Suggestions */}
      {isOpen && (
        <div className={styles.dropdown}>
          <div className={styles.dropdownHeader}>
            <span>Suggested Locations</span>
            {isLoading && <span>Searching…</span>}
          </div>

          {suggestions.length > 0 ? (
            <div className={styles.suggestionList}>
              {suggestions.map((item, index) => {
                const isSelected = selectedIndex === index;
                return (
                  <button
                    key={item.id}
                    type="button"
                    className={`${styles.suggestionItem} ${isSelected ? styles.suggestionItemActive : ''}`}
                    onClick={() => handleSelect(item)}
                    onMouseEnter={() => setSelectedIndex(index)}
                  >
                    <div className={styles.suggestionIconWrap}>
                      <MapPin size={14} />
                    </div>
                    <div className={styles.suggestionText}>
                      <span className={styles.suggestionName}>{item.name}</span>
                      {item.subtitle && (
                        <span className={styles.suggestionSubtitle}>{item.subtitle}</span>
                      )}
                    </div>
                    {value === item.fullName && <Check size={14} color="var(--panel-2)" />}
                  </button>
                );
              })}
            </div>
          ) : (
            <div className={styles.noResults}>
              <span>No locations found for "{query}"</span>
            </div>
          )}
        </div>
      )}

      {/* Selected location tag indicator */}
      {value && !isOpen && (
        <div className={styles.selectedBadge}>
          <Navigation size={12} />
          <span>{value}</span>
          <button type="button" className={styles.selectedBadgeRemove} onClick={handleClear} title="Remove location">
            <X size={11} />
          </button>
        </div>
      )}
    </div>
  );
}
