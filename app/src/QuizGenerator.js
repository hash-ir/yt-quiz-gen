import React, { useState } from 'react';
import { Button, TextField, Select, MenuItem, FormControl, InputLabel, RadioGroup, FormControlLabel, Radio, Typography, Paper, Box } from '@mui/material';

const QuizGenerator = () => {
  const [url, setUrl] = useState('');
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState('');
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState(Array(5).fill(''));
  const [quizReport, setQuizReport] = useState('');
  const [showTopics, setShowTopics] = useState(false);
  const [showQuestions, setShowQuestions] = useState(false);
  const [showContinue, setShowContinue] = useState(false);
  const [showQuit, setShowQuit] = useState(false);
  const [showReport, setShowReport] = useState(false);

  const handleUrlSubmit = () => {
    // Simulating topic extraction
    const extractedTopics = ['Topic 1', 'Topic 2', 'Topic 3'];
    setTopics(extractedTopics);
    setShowTopics(true);
  };

  const handleTopicSelect = () => {
    // Simulating quiz generation
    const generatedQuestions = [
      { question: 'Question 1?', options: ['A', 'B', 'C', 'D'] },
      { question: 'Question 2?', options: ['A', 'B', 'C', 'D'] },
      { question: 'Question 3?', options: ['A', 'B', 'C', 'D'] },
      { question: 'Question 4?', options: ['A', 'B', 'C', 'D'] },
      { question: 'Question 5?', options: ['A', 'B', 'C', 'D'] },
    ];
    setQuestions(generatedQuestions);
    setShowQuestions(true);
    setShowContinue(true);
  };

  const handleContinue = () => {
    // Simulating new questions generation
    const newQuestions = [
      { question: 'New Question 1?', options: ['A', 'B', 'C', 'D'] },
      { question: 'New Question 2?', options: ['A', 'B', 'C', 'D'] },
      { question: 'New Question 3?', options: ['A', 'B', 'C', 'D'] },
      { question: 'New Question 4?', options: ['A', 'B', 'C', 'D'] },
      { question: 'New Question 5?', options: ['A', 'B', 'C', 'D'] },
    ];
    setQuestions(newQuestions);
    setAnswers(Array(5).fill(''));
    setShowQuit(true);
  };

  const handleQuit = () => {
    // Simulating quiz report generation
    const report = `
      ## Question 1
      **Correct**.
      **Explanation**: Explanation for question 1.

      ## Question 2
      **Incorrect**. The correct answer is B.
      **Explanation**: Explanation for question 2.

      ## Question 3
      **Correct**.
      **Explanation**: Explanation for question 3.

      ## Question 4
      **Correct**.
      **Explanation**: Explanation for question 4.

      ## Question 5
      **Incorrect**. The correct answer is A.
      **Explanation**: Explanation for question 5.

      ### Final Score: **3/5**
    `;
    setQuizReport(report);
    setShowReport(true);
    setShowQuestions(false);
    setShowContinue(false);
    setShowQuit(false);
  };

  const handleClear = () => {
    setUrl('');
    setTopics([]);
    setSelectedTopic('');
    setQuestions([]);
    setAnswers(Array(5).fill(''));
    setQuizReport('');
    setShowTopics(false);
    setShowQuestions(false);
    setShowContinue(false);
    setShowQuit(false);
    setShowReport(false);
  };

  return (
    <Box sx={{ maxWidth: 600, margin: 'auto', padding: 2 }}>
      <Typography variant="h4" gutterBottom>
        YouTube Quiz Generator
      </Typography>
      
      <Paper elevation={3} sx={{ padding: 2, marginBottom: 2 }}>
        <TextField
          fullWidth
          label="YouTube Video URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          margin="normal"
        />
        <Box sx={{ display: 'flex', justifyContent: 'space-between', marginTop: 2 }}>
          <Button variant="contained" onClick={handleUrlSubmit}>
            Submit
          </Button>
          <Button variant="outlined" onClick={handleClear}>
            Clear
          </Button>
        </Box>
      </Paper>

      {showTopics && (
        <Paper elevation={3} sx={{ padding: 2, marginBottom: 2 }}>
          <FormControl fullWidth margin="normal">
            <InputLabel>Select a topic to start quizzing</InputLabel>
            <Select
              value={selectedTopic}
              onChange={(e) => setSelectedTopic(e.target.value)}
            >
              {topics.map((topic, index) => (
                <MenuItem key={index} value={topic}>
                  {topic}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Button variant="contained" onClick={handleTopicSelect} sx={{ marginTop: 2 }}>
            Start Quiz
          </Button>
        </Paper>
      )}

      {showQuestions && (
        <Paper elevation={3} sx={{ padding: 2, marginBottom: 2 }}>
          {questions.map((q, index) => (
            <FormControl component="fieldset" key={index} margin="normal">
              <Typography variant="subtitle1">{q.question}</Typography>
              <RadioGroup
                value={answers[index]}
                onChange={(e) => {
                  const newAnswers = [...answers];
                  newAnswers[index] = e.target.value;
                  setAnswers(newAnswers);
                }}
              >
                {q.options.map((option, optionIndex) => (
                  <FormControlLabel
                    key={optionIndex}
                    value={option}
                    control={<Radio />}
                    label={option}
                  />
                ))}
              </RadioGroup>
            </FormControl>
          ))}
          {showContinue && (
            <Button variant="contained" onClick={handleContinue} sx={{ marginTop: 2 }}>
              Continue
            </Button>
          )}
          {showQuit && (
            <Button variant="contained" color="error" onClick={handleQuit} sx={{ marginTop: 2, marginLeft: 2 }}>
              Quit
            </Button>
          )}
        </Paper>
      )}

      {showReport && (
        <Paper elevation={3} sx={{ padding: 2 }}>
          <Typography variant="h6" gutterBottom>
            Quiz Report
          </Typography>
          <Typography component="div" dangerouslySetInnerHTML={{ __html: quizReport }} />
        </Paper>
      )}
    </Box>
  );
};

export default QuizGenerator;