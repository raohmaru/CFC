files = Dir.glob("*.png")

files.each { |file|
  # next if file =~ /Capcom|SNK/
  name = file[0..-5]
  # puts <<eof
		# <block type="overlay" id="subtype_#{name.downcase}" src="Proxy/Subtypes/#{file}">
			# <location x="310" y="446" />
		# </block>
# eof

  puts <<eof
					<case value="#{name}" break="True">
						<link block="subtype_#{name.downcase.gsub(' ', '_')}" />
					</case>
eof
}