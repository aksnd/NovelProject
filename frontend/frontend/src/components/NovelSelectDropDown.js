import React, { useState, useEffect } from 'react';
import Select from 'react-select';

export default function NovelSelect({ onSelect }) {
  const [options, setOptions] = useState([]);

  useEffect(() => {
    async function fetchNovels() {
      const res = await fetch('http://3.36.221.36:8000/api/novels/'); // 전체 소설 목록을 가져오는 API
      if (!res.ok) {
        throw new Error(`HTTP error! Status: ${res.status}`);
      }
      const novels = await res.json();
      const options = novels.map(novel => ({
        value: novel.id,
        label: novel.title,
      }));
      setOptions(options);
    }

    fetchNovels();
  }, []);

  const customStyles = {
    container: (provided) => ({
      ...provided,
      width: '100%',
      maxWidth: '500px',
      margin: '0 auto',
    }),
    control: (provided) => ({
      ...provided,
      height: '40px',
      minHeight: '40px',
      fontSize: '16px',
    }),
    menu: (provided) => ({
      ...provided,
      zIndex: 9999,
    }),
    placeholder: (provided) => ({
      ...provided,
      fontSize: '16px',
    }),
  };

  return (
    <Select
      options={options}
      onChange={option => onSelect(option)}
      placeholder="Select a novel..."
      styles={customStyles}
    />
  );
}
