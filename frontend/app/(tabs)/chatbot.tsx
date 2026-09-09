import React, { useState, useRef, useEffect } from 'react';
import {
  View, Text, ScrollView, StyleSheet, TouchableOpacity,
  TextInput, KeyboardAvoidingView, Platform, Animated, ActivityIndicator,
} from 'react-native';
import { colors, radius } from '../../constants/theme';
import { sendChatMessage } from '../../services/api';

interface Message { id: string; role: 'user' | 'assistant'; text: string; }

const WELCOME: Message = {
  id: '0',
  role: 'assistant',
  text: "Hi! I'm BizMate AI. Ask me about your sales, stock, expiry, profit, or forecasts.",
};

export default function Chatbot() {
  const [messages, setMessages] = useState<Message[]>([WELCOME]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<ScrollView>(null);
  const dotAnim = useRef(new Animated.Value(0)).current;
  const animRef = useRef<Animated.CompositeAnimation | null>(null);

  useEffect(() => {
    if (isTyping) {
      animRef.current = Animated.loop(
        Animated.sequence([
          Animated.timing(dotAnim, { toValue: 1, duration: 500, useNativeDriver: true }),
          Animated.timing(dotAnim, { toValue: 0, duration: 500, useNativeDriver: true }),
        ])
      );
      animRef.current.start();
    } else {
      animRef.current?.stop();
      dotAnim.setValue(0);
    }
  }, [isTyping]);

  const scrollToEnd = () =>
    setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 100);

  const send = async (text?: string) => {
    const msgText = (text || input).trim();
    if (!msgText || isTyping) return;

    const userMsg: Message = { id: Date.now().toString(), role: 'user', text: msgText };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);
    scrollToEnd();

    const res = await sendChatMessage(msgText);

    setIsTyping(false);
    const botMsg: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      text: res,
    };
    setMessages(prev => [...prev, botMsg]);
    scrollToEnd();
  };

  // ✅ Handles Enter key press from keyboard
  const handleKeyPress = ({ nativeEvent }: { nativeEvent: { key: string } }) => {
    if (nativeEvent.key === 'Enter') {
      send();
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={90}
    >
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.botAvatar}>
          <Text style={{ fontSize: 24 }}>🤖</Text>
        </View>
        <View>
          <Text style={styles.botName}>BizMate AI</Text>
          <View style={styles.onlineRow}>
            <View style={styles.onlineDot} />
            <Text style={styles.onlineText}>Online · Gemini powered</Text>
          </View>
        </View>
      </View>
      {/* Accent line — mirrors dashboard card colored borders */}
<View style={{ height: 2, backgroundColor: '#1a6bcc', opacity: 0.7 }} />
      {/* Messages */}
      <ScrollView
        ref={scrollRef}
        style={styles.messages}
        showsVerticalScrollIndicator={false}
        onContentSizeChange={scrollToEnd}
      >
       {messages.map(m => (
  <View key={m.id} style={[styles.bubble, m.role === 'user' ? styles.userBubble : styles.botBubble]}>
  {m.role === 'user' ? (
    // User bubble — no avatar, no row wrapper needed
    <View style={[styles.bubbleInner, styles.userBubbleInner]}>
      <Text style={[styles.bubbleText, styles.userBubbleText]}>
        {m.text}
      </Text>
    </View>
  ) : (
    // Bot bubble — avatar + bubble side by side
    <View style={{ flexDirection: 'row', alignItems: 'flex-end', gap: 8 }}>
      <View style={styles.botAvatarSmall}>
        <Text style={{ fontSize: 14 }}>🤖</Text>
      </View>
      <View style={[styles.bubbleInner, styles.botBubbleInner]}>
        <Text style={styles.bubbleText}>
          {m.text}
        </Text>
      </View>
    </View>
  )}
</View>
))}

        {/* Typing indicator */}
        {isTyping && (
  <View style={[styles.bubble, styles.botBubble]}>
    <View style={{ flexDirection: 'row', alignItems: 'flex-end', gap: 8 }}>
      <View style={styles.botAvatarSmall}>
        <Text style={{ fontSize: 14 }}>🤖</Text>
      </View>
      <View style={styles.typingBubble}>
        {[0, 1, 2].map(i => (
          <Animated.View key={i} style={[styles.dot, { opacity: dotAnim, marginLeft: i * 6 }]} />
        ))}
      </View>
    </View>
  </View>
)}
      </ScrollView>

      {/* Input */}
      <View style={styles.inputRow}>
        <TextInput
          style={styles.textInput}
          placeholder="Ask about your business..."
          placeholderTextColor={colors.textSub}
          value={input}
          onChangeText={setInput}
          multiline
          returnKeyType="send"                      // ✅ Shows "Send" on keyboard
          onSubmitEditing={() => send()}             // ✅ Triggers on Enter/Send tap
          onKeyPress={handleKeyPress}                // ✅ Catches physical Enter key
          blurOnSubmit={false}                       // ✅ Keeps keyboard open after send
          editable={!isTyping}
        />
        <TouchableOpacity
          style={[styles.sendBtn, (!input.trim() || isTyping) && styles.sendBtnDisabled]}
          onPress={() => send()}
          disabled={!input.trim() || isTyping}
        >
          {isTyping
            ? <ActivityIndicator color="#fff" size="small" />
            : <Text style={styles.sendBtnText}>➤</Text>
          }
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0d1117' },   // dark navy bg
botAvatarSmall: {
  width: 28, height: 28, borderRadius: 14,
  backgroundColor: '#1e2d45',
  alignItems: 'center', justifyContent: 'center',
  borderWidth: 1, borderColor: '#2a3f5f',
},
  // Header — dark card like dashboard panels
  header: {
    flexDirection: 'row', alignItems: 'center', gap: 12,
    backgroundColor: '#131c2e',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#1e2d45',
  },
  botAvatar: {
    width: 48, height: 48, borderRadius: 24,
    backgroundColor: '#1e2d45',
    alignItems: 'center', justifyContent: 'center',
    borderWidth: 1, borderColor: '#2a3f5f',
  },
  botName: { fontSize: 16, fontWeight: '800', color: '#ffffff' },
  onlineRow: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 2 },
  onlineDot: { width: 7, height: 7, borderRadius: 3.5, backgroundColor: '#00e5a0' }, // green accent
  onlineText: { fontSize: 11, color: '#6b82a8' },

  // Messages area
  messages: { flex: 1, padding: 14, backgroundColor: '#0d1117' },
  bubble: { marginBottom: 16 },
  userBubble: { alignItems: 'flex-end' },
  botBubble: { alignItems: 'flex-start' },

  bubbleInner: { maxWidth: '80%', borderRadius: 14, padding: 12 },

  // User bubble — uses blue accent matching dashboard's blue chart color
  userBubbleInner: {
    backgroundColor: '#1a6bcc',
    borderBottomRightRadius: 4,
  },

  // Bot bubble — dark card surface like dashboard panels
  botBubbleInner: {
    backgroundColor: '#131c2e',
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: '#1e2d45',
  },

  bubbleText: { fontSize: 14, color: '#a8b8d0', lineHeight: 20 },
  userBubbleText: { color: '#ffffff' },

  // Typing dots
  typingBubble: {
    backgroundColor: '#131c2e',
    borderRadius: 14, borderBottomLeftRadius: 4,
    padding: 16, flexDirection: 'row', alignItems: 'center',
    borderWidth: 1, borderColor: '#1e2d45',
  },
  dot: { width: 7, height: 7, borderRadius: 3.5, backgroundColor: '#6b82a8' },

  // Input row
  inputRow: {
    flexDirection: 'row', gap: 10, padding: 14,
    backgroundColor: '#131c2e',
    borderTopWidth: 1, borderTopColor: '#1e2d45',
  },
  textInput: {
    flex: 1,
    borderWidth: 1.5, borderColor: '#1e2d45',
    borderRadius: 12,
    padding: 12,
    fontSize: 14,
    color: '#ffffff',
    maxHeight: 100,
    backgroundColor: '#0d1117',
  },

  // Send button — blue accent
  sendBtn: {
    width: 46, height: 46, borderRadius: 23,
    backgroundColor: '#1a6bcc',
    alignItems: 'center', justifyContent: 'center',
  },
  sendBtnDisabled: { backgroundColor: '#1e2d45' },
  sendBtnText: { color: '#fff', fontSize: 16 },
});